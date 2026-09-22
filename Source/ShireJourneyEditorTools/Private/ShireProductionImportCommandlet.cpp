#include "ShireProductionImportCommandlet.h"

#include "AssetImportTask.h"
#include "AssetRegistryModule.h"
#include "AssetToolsModule.h"
#include "FileHelpers.h"
#include "Factories/FbxImportUI.h"
#include "Factories/FbxStaticMeshImportData.h"
#include "Factories/MaterialInstanceConstantFactoryNew.h"
#include "Factories/MaterialFactoryNew.h"
#include "Engine/StaticMesh.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformFilemanager.h"
#include "Misc/FileHelper.h"
#include "Misc/PackageName.h"
#include "Misc/Paths.h"
#include "Materials/Material.h"
#include "Materials/MaterialExpressionScalarParameter.h"
#include "Materials/MaterialExpressionVectorParameter.h"
#include "Materials/MaterialInterface.h"
#include "Materials/MaterialInstanceConstant.h"
#include "Modules/ModuleManager.h"
#include "UObject/Package.h"
#include "UObject/UObjectGlobals.h"

UShireProductionImportCommandlet::UShireProductionImportCommandlet()
{
    IsClient = false;
    IsServer = false;
    IsEditor = true;
    LogToConsole = true;
    ShowErrorCount = true;
}

int32 UShireProductionImportCommandlet::Main(const FString& Params)
{
    const FString SourceRoot = FPaths::ConvertRelativePathToFull(
        FPaths::Combine(FPaths::ProjectDir(), TEXT("SourceAssets/Production")));
    const FString WorkingRoot = FPaths::ConvertRelativePathToFull(
        FPaths::Combine(FPaths::ProjectSavedDir(), TEXT("ShireProductionImportWorking")));

    // Never normalize/import directly from tracked SourceAssets. The older path
    // injected smoothing-group text into real .obj source files, which made
    // GitHub Desktop show hundreds/thousands of local changes after one-click
    // import. Work on an ignored Saved/ copy so source assets stay byte-stable.
    IFileManager::Get().DeleteDirectory(*WorkingRoot, false, true);
    IPlatformFile& PlatformFile = FPlatformFileManager::Get().GetPlatformFile();
    if (!PlatformFile.CopyDirectoryTree(*WorkingRoot, *SourceRoot, true))
    {
        UE_LOG(LogTemp, Error, TEXT("ShireProductionImport: failed to create working copy %s from %s"), *WorkingRoot, *SourceRoot);
        return 4;
    }

    TArray<FString> SourceFiles;
    TArray<FString> TextureFiles;
    TArray<FString> MeshFiles;
    TArray<FString> MaterialLibraryFiles;
    IFileManager::Get().FindFilesRecursive(TextureFiles, *WorkingRoot, TEXT("*.png"), true, false, false);\n    IFileManager::Get().FindFilesRecursive(TextureFiles, *WorkingRoot, TEXT("*.tga"), true, false, false);
    IFileManager::Get().FindFilesRecursive(MeshFiles, *WorkingRoot, TEXT("*.obj"), true, false, false);
    IFileManager::Get().FindFilesRecursive(MaterialLibraryFiles, *WorkingRoot, TEXT("*.mtl"), true, false, false);
    TextureFiles.Sort();
    MeshFiles.Sort();
    MaterialLibraryFiles.Sort();
    SourceFiles.Append(TextureFiles);
    SourceFiles.Append(MeshFiles);

    if (SourceFiles.Num() == 0)
    {
        UE_LOG(LogTemp, Warning, TEXT("ShireProductionImport: no production assets found at %s"), *SourceRoot);
        return 0;
    }

    FAssetToolsModule& AssetTools = FModuleManager::LoadModuleChecked<FAssetToolsModule>(TEXT("AssetTools"));
    int32 Failed = 0;
    TArray<UPackage*> ImportedMaterialPackages;

    auto SaveMaterialPackagesDeterministically = [&](const TCHAR* Phase) -> bool
    {
        int32 SavedPackages = 0;
        int32 SaveFailures = 0;

        for (UPackage* Package : ImportedMaterialPackages)
        {
            if (!Package || Package == GetTransientPackage())
            {
                continue;
            }

            const FString LongPackageName = Package->GetName();
            const FString AssetName = FPackageName::GetLongPackageAssetName(LongPackageName);
            const FString PackageFilename = FPackageName::LongPackageNameToFilename(
                LongPackageName,
                FPackageName::GetAssetPackageExtension());

            IFileManager::Get().MakeDirectory(*FPaths::GetPath(PackageFilename), true);
            Package->MarkPackageDirty();

            UObject* AssetObject = FindObject<UObject>(Package, *AssetName);
            const bool bSaved = UPackage::SavePackage(
                Package,
                AssetObject,
                RF_Public | RF_Standalone,
                *PackageFilename,
                GError,
                nullptr,
                false,
                true,
                SAVE_NoError);

            const bool bExistsOnDisk = IFileManager::Get().FileExists(*PackageFilename);
            if (!bSaved || !bExistsOnDisk)
            {
                ++SaveFailures;
                ++Failed;
                UE_LOG(
                    LogTemp,
                    Error,
                    TEXT("ShireProductionImport material save FAILED: phase=%s package=%s file=%s saved=%s exists=%s"),
                    Phase,
                    *LongPackageName,
                    *PackageFilename,
                    bSaved ? TEXT("yes") : TEXT("no"),
                    bExistsOnDisk ? TEXT("yes") : TEXT("no"));
            }
            else
            {
                ++SavedPackages;
            }
        }

        UE_LOG(
            LogTemp,
            Display,
            TEXT("ShireProductionImport deterministic material save: phase=%s saved=%d failures=%d packages=%d"),
            Phase,
            SavedPackages,
            SaveFailures,
            ImportedMaterialPackages.Num());

        return SaveFailures == 0;
    };

    // UE4.27 unattended OBJ import does not reliably persist simple MTL-created
    // material packages. Create a deterministic project-owned master surface first,
    // then bind authored MTL instances to it. This gives production geometry a real
    // roughness/metallic response while preserving the lightweight flat-color bank.
    const TCHAR* ProductionSurfacePath =
        TEXT("/Game/Production/Materials/M_ProductionSurface.M_ProductionSurface");
    UMaterialInterface* ProductionMaterialParent =
        LoadObject<UMaterialInterface>(nullptr, ProductionSurfacePath);

    if (!ProductionMaterialParent)
    {
        UMaterialFactoryNew* SurfaceFactory = NewObject<UMaterialFactoryNew>();
        UMaterial* SurfaceMaterial = Cast<UMaterial>(
            AssetTools.Get().CreateAsset(
                TEXT("M_ProductionSurface"),
                TEXT("/Game/Production/Materials"),
                UMaterial::StaticClass(),
                SurfaceFactory));

        if (SurfaceMaterial)
        {
            UMaterialExpressionVectorParameter* ColorParameter =
                NewObject<UMaterialExpressionVectorParameter>(SurfaceMaterial);
            ColorParameter->ParameterName = TEXT("Color");
            ColorParameter->DefaultValue = FLinearColor(0.35f, 0.35f, 0.35f, 1.0f);
            SurfaceMaterial->Expressions.Add(ColorParameter);
            SurfaceMaterial->BaseColor.Expression = ColorParameter;

            UMaterialExpressionScalarParameter* RoughnessParameter =
                NewObject<UMaterialExpressionScalarParameter>(SurfaceMaterial);
            RoughnessParameter->ParameterName = TEXT("Roughness");
            RoughnessParameter->DefaultValue = 0.68f;
            SurfaceMaterial->Expressions.Add(RoughnessParameter);
            SurfaceMaterial->Roughness.Expression = RoughnessParameter;

            UMaterialExpressionScalarParameter* MetallicParameter =
                NewObject<UMaterialExpressionScalarParameter>(SurfaceMaterial);
            MetallicParameter->ParameterName = TEXT("Metallic");
            MetallicParameter->DefaultValue = 0.0f;
            SurfaceMaterial->Expressions.Add(MetallicParameter);
            SurfaceMaterial->Metallic.Expression = MetallicParameter;

            SurfaceMaterial->PostEditChange();
            SurfaceMaterial->MarkPackageDirty();
            ImportedMaterialPackages.AddUnique(SurfaceMaterial->GetOutermost());
            ProductionMaterialParent = SurfaceMaterial;
            UE_LOG(LogTemp, Display, TEXT("ShireProductionImport created M_ProductionSurface master material."));
        }
        else
        {
            ++Failed;
            UE_LOG(LogTemp, Error, TEXT("ShireProductionImport failed to create M_ProductionSurface master material."));
        }
    }

    int32 SynthesizedMaterialAssets = 0;

    if (ProductionMaterialParent)
    {
        for (const FString& MtlFilename : MaterialLibraryFiles)
        {
            FString RelativeMtl = MtlFilename;
            FPaths::MakePathRelativeTo(RelativeMtl, *(WorkingRoot / TEXT("")));
            RelativeMtl.ReplaceInline(TEXT("\\"), TEXT("/"));
            const FString RelativeDir = FPaths::GetPath(RelativeMtl);
            const FString DestinationPath = RelativeDir.IsEmpty()
                ? TEXT("/Game/Production")
                : FString::Printf(TEXT("/Game/Production/%s"), *RelativeDir);

            FString MtlText;
            if (!FFileHelper::LoadFileToString(MtlText, *MtlFilename))
            {
                UE_LOG(LogTemp, Warning, TEXT("ShireProductionImport: could not read MTL %s"), *MtlFilename);
                continue;
            }

            TArray<FString> Lines;
            MtlText.ParseIntoArrayLines(Lines, true);
            FString CurrentMaterialName;
            FLinearColor CurrentBaseColor(0.35f, 0.35f, 0.35f, 1.0f);
            float CurrentRoughness = 0.68f;
            float CurrentMetallic = 0.0f;

            auto FlushMaterial = [&]()
            {
                if (CurrentMaterialName.IsEmpty())
                {
                    return;
                }

                const FString ObjectPath = FString::Printf(
                    TEXT("%s/%s.%s"),
                    *DestinationPath,
                    *CurrentMaterialName,
                    *CurrentMaterialName);

                const FString PackageName = FString::Printf(
                    TEXT("%s/%s"),
                    *DestinationPath,
                    *CurrentMaterialName);

                UMaterialInstanceConstant* Instance =
                    FindObject<UMaterialInstanceConstant>(nullptr, *ObjectPath);

                if (!Instance && FPackageName::DoesPackageExist(PackageName))
                {
                    Instance = LoadObject<UMaterialInstanceConstant>(nullptr, *ObjectPath);
                }

                if (!Instance)
                {
                    UMaterialInstanceConstantFactoryNew* Factory =
                        NewObject<UMaterialInstanceConstantFactoryNew>();
                    Factory->InitialParent = ProductionMaterialParent;
                    Instance = Cast<UMaterialInstanceConstant>(
                        AssetTools.Get().CreateAsset(
                            CurrentMaterialName,
                            DestinationPath,
                            UMaterialInstanceConstant::StaticClass(),
                            Factory));
                }

                if (Instance)
                {
                    Instance->SetParentEditorOnly(ProductionMaterialParent);
                    Instance->SetVectorParameterValueEditorOnly(
                        FMaterialParameterInfo(TEXT("Color")),
                        CurrentBaseColor);
                    Instance->SetScalarParameterValueEditorOnly(
                        FMaterialParameterInfo(TEXT("Roughness")),
                        FMath::Clamp(CurrentRoughness, 0.0f, 1.0f));
                    Instance->SetScalarParameterValueEditorOnly(
                        FMaterialParameterInfo(TEXT("Metallic")),
                        FMath::Clamp(CurrentMetallic, 0.0f, 1.0f));
                    Instance->PostEditChange();
                    Instance->MarkPackageDirty();
                    ImportedMaterialPackages.AddUnique(Instance->GetOutermost());
                    ++SynthesizedMaterialAssets;
                }
                else
                {
                    ++Failed;
                    UE_LOG(
                        LogTemp,
                        Error,
                        TEXT("ShireProductionImport: failed to synthesize material %s/%s"),
                        *DestinationPath,
                        *CurrentMaterialName);
                }
            };

            for (const FString& RawLine : Lines)
            {
                const FString Line = RawLine.TrimStartAndEnd();
                if (Line.StartsWith(TEXT("newmtl "), ESearchCase::IgnoreCase))
                {
                    FlushMaterial();
                    CurrentMaterialName = Line.Mid(7).TrimStartAndEnd();
                    CurrentBaseColor = FLinearColor(0.35f, 0.35f, 0.35f, 1.0f);
                    CurrentRoughness = 0.68f;
                    CurrentMetallic = 0.0f;
                }
                else if (Line.StartsWith(TEXT("Kd "), ESearchCase::IgnoreCase) &&
                    !CurrentMaterialName.IsEmpty())
                {
                    TArray<FString> Parts;
                    Line.ParseIntoArrayWS(Parts);
                    if (Parts.Num() >= 4)
                    {
                        CurrentBaseColor = FLinearColor(
                            FCString::Atof(*Parts[1]),
                            FCString::Atof(*Parts[2]),
                            FCString::Atof(*Parts[3]),
                            1.0f);
                    }
                }
                else if (Line.StartsWith(TEXT("Pr "), ESearchCase::IgnoreCase) &&
                    !CurrentMaterialName.IsEmpty())
                {
                    TArray<FString> Parts;
                    Line.ParseIntoArrayWS(Parts);
                    if (Parts.Num() >= 2)
                    {
                        CurrentRoughness = FCString::Atof(*Parts[1]);
                    }
                }
                else if (Line.StartsWith(TEXT("Pm "), ESearchCase::IgnoreCase) &&
                    !CurrentMaterialName.IsEmpty())
                {
                    TArray<FString> Parts;
                    Line.ParseIntoArrayWS(Parts);
                    if (Parts.Num() >= 2)
                    {
                        CurrentMetallic = FCString::Atof(*Parts[1]);
                    }
                }
            }
            FlushMaterial();
        }

        if (ImportedMaterialPackages.Num() > 0)
        {
            SaveMaterialPackagesDeterministically(TEXT("pre-mesh-import"));
        }

        UE_LOG(
            LogTemp,
            Display,
            TEXT("ShireProductionImport synthesized authored materials: libraries=%d assets=%d packages=%d"),
            MaterialLibraryFiles.Num(),
            SynthesizedMaterialAssets,
            ImportedMaterialPackages.Num());
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("ShireProductionImport: production material parent missing"));
        ++Failed;
    }
    TSet<FString> AuthoredMaterialDestinationPaths;
    int32 RecoveredMaterialBindings = 0;

    for (const FString& Filename : SourceFiles)
    {
        FString Relative = Filename;
        FPaths::MakePathRelativeTo(Relative, *(WorkingRoot / TEXT("")));
        Relative.ReplaceInline(TEXT("\\"), TEXT("/"));

        const FString RelativeDir = FPaths::GetPath(Relative);
        const FString DestinationPath = RelativeDir.IsEmpty()
            ? TEXT("/Game/Production")
            : FString::Printf(TEXT("/Game/Production/%s"), *RelativeDir);

        UAssetImportTask* Task = NewObject<UAssetImportTask>();
        Task->Filename = Filename;
        Task->DestinationPath = DestinationPath;
        Task->DestinationName = FPaths::GetBaseFilename(Filename);
        Task->bAutomated = true;
        Task->bSave = true;
        Task->bReplaceExisting = true;

        bool bBareObjMaterialImportDisabled = false;
        bool bInjectedSmoothingGroup = false;
        bool bAuthoredMaterialImportForced = false;
        bool bBuiltInTangentsForUntexturedObj = false;
        TArray<FString> AuthoredMaterialNames;
        if (FPaths::GetExtension(Filename).Equals(TEXT("obj"), ESearchCase::IgnoreCase))
        {
            FString ObjSource;
            if (FFileHelper::LoadFileToString(ObjSource, *Filename))
            {
                // The production bank is intentionally lightweight, but UE4.27 emits
                // hundreds of warnings when OBJ files omit an explicit smoothing group.
                // Filename points into the ignored Saved/ working copy, so this
                // normalization can never dirty tracked SourceAssets.
                const bool bHasSmoothing =
                    ObjSource.StartsWith(TEXT("s ")) ||
                    ObjSource.Contains(TEXT("\ns "), ESearchCase::CaseSensitive);
                if (!bHasSmoothing)
                {
                    int32 FaceLine = ObjSource.Find(TEXT("\nf "), ESearchCase::CaseSensitive);
                    if (FaceLine != INDEX_NONE)
                    {
                        ObjSource.InsertAt(FaceLine + 1, TEXT("s 1\n"));
                        if (FFileHelper::SaveStringToFile(ObjSource, *Filename))
                        {
                            bInjectedSmoothingGroup = true;
                        }
                    }
                }

                const bool bHasMaterialLibrary =
                    ObjSource.Contains(TEXT("mtllib "), ESearchCase::IgnoreCase);

                // UE4.27 can collapse OBJ material slots to "defaultMat" when automated
                // material creation is disabled, even though the source has valid usemtl
                // statements. Preserve the authored material order from the OBJ so we
                // can deterministically repair those slots after mesh import.
                if (bHasMaterialLibrary)
                {
                    TArray<FString> ObjLines;
                    ObjSource.ParseIntoArrayLines(ObjLines, true);
                    for (const FString& RawObjLine : ObjLines)
                    {
                        const FString ObjLine = RawObjLine.TrimStartAndEnd();
                        if (!ObjLine.StartsWith(TEXT("usemtl "), ESearchCase::IgnoreCase))
                        {
                            continue;
                        }

                        const FString MaterialName = ObjLine.Mid(7).TrimStartAndEnd();
                        if (!MaterialName.IsEmpty() && !AuthoredMaterialNames.Contains(MaterialName))
                        {
                            AuthoredMaterialNames.Add(MaterialName);
                        }
                    }
                }

                // Do not depend on factory defaults in unattended UE4.27 imports.
                // Authored OBJ/MTL pairs must explicitly create material assets;
                // bare character/proxy OBJ files must explicitly avoid placeholder
                // material references.
                UFbxImportUI* ImportOptions = NewObject<UFbxImportUI>();
                // MTL definitions are synthesized above into deterministic material
                // instances. Disable FBX/OBJ material creation here to prevent UE4.27
                // from emitting transient/broken duplicate package references.
                ImportOptions->bImportMaterials = false;
                ImportOptions->bImportTextures = false;
                if (ImportOptions->StaticMeshImportData)
                {
                    ImportOptions->StaticMeshImportData->bRemoveDegenerates = true;

                    const bool bHasTextureCoordinates =
                        ObjSource.StartsWith(TEXT("vt ")) ||
                        ObjSource.Contains(TEXT("\nvt "), ESearchCase::CaseSensitive);

                    // MikkTSpace derives tangent space from texture UVs. The current
                    // lightweight production OBJ bank is mostly flat-color geometry
                    // with no vt records, so forcing MikkTSpace only creates invalid
                    // tangent/binormal warnings without adding useful shading data.
                    // Compute clean normals/tangents with UE4's built-in generator for
                    // those untextured meshes; textured meshes keep the default path.
                    if (!bHasTextureCoordinates)
                    {
                        ImportOptions->StaticMeshImportData->NormalImportMethod =
                            EFBXNormalImportMethod::FBXNIM_ComputeNormals;
                        ImportOptions->StaticMeshImportData->NormalGenerationMethod =
                            EFBXNormalGenerationMethod::BuiltIn;
                        bBuiltInTangentsForUntexturedObj = true;
                    }
                }
                Task->Options = ImportOptions;

                bBareObjMaterialImportDisabled = !bHasMaterialLibrary;
                bAuthoredMaterialImportForced = bHasMaterialLibrary;
                if (bHasMaterialLibrary)
                {
                    AuthoredMaterialDestinationPaths.Add(DestinationPath);
                }
            }
        }

        TArray<UAssetImportTask*> Tasks;
        Tasks.Add(Task);
        AssetTools.Get().ImportAssetTasks(Tasks);

        const FString AssetName = FPaths::GetBaseFilename(Filename);
        const FString ExpectedObjectPath = FString::Printf(
            TEXT("%s/%s.%s"), *DestinationPath, *AssetName, *AssetName);
        UObject* ImportedAsset = LoadObject<UObject>(nullptr, *ExpectedObjectPath);

        int32 MarkedMaterialPackages = 0;
        if (UStaticMesh* ImportedMesh = Cast<UStaticMesh>(ImportedAsset))
        {
            // OBJ/MTL import can leave material packages referenced by the mesh without
            // flagging those secondary packages for persistence. Mark every real
            // imported material package dirty so the final SaveDirtyPackages pass writes
            // the mesh and its material dependencies together.
            TArray<FStaticMaterial>& StaticMaterials = ImportedMesh->GetStaticMaterials();
            for (int32 MaterialIndex = 0; MaterialIndex < StaticMaterials.Num(); ++MaterialIndex)
            {
                FStaticMaterial& StaticMaterial = StaticMaterials[MaterialIndex];
                UMaterialInterface* Material = StaticMaterial.MaterialInterface;

                // When UE4.27 collapses valid authored OBJ slots to defaultMat in
                // unattended mode, restore the slot identity from source usemtl order.
                if (bAuthoredMaterialImportForced &&
                    AuthoredMaterialNames.IsValidIndex(MaterialIndex))
                {
                    const FString CurrentSlotName = StaticMaterial.MaterialSlotName.ToString();
                    if (StaticMaterial.MaterialSlotName.IsNone() ||
                        CurrentSlotName.Equals(TEXT("defaultMat"), ESearchCase::IgnoreCase))
                    {
                        const FName AuthoredSlotName(*AuthoredMaterialNames[MaterialIndex]);
                        StaticMaterial.MaterialSlotName = AuthoredSlotName;
                        StaticMaterial.ImportedMaterialSlotName = AuthoredSlotName;
                    }
                }

                // UE4.27 OBJ import can serialize the material package path into the
                // mesh while leaving MaterialInterface unresolved in unattended mode.
                // Recover the material object by the imported slot name immediately,
                // then save both sides of the reference in the same commandlet run.
                if (bAuthoredMaterialImportForced && !StaticMaterial.MaterialSlotName.IsNone())
                {
                    const FString SlotName = StaticMaterial.MaterialSlotName.ToString();
                    const FString CandidateObjectPath = FString::Printf(
                        TEXT("%s/%s.%s"),
                        *DestinationPath,
                        *SlotName,
                        *SlotName);
                    UMaterialInterface* AuthoredMaterial =
                        FindObject<UMaterialInterface>(nullptr, *CandidateObjectPath);

                    if (!AuthoredMaterial)
                    {
                        const FString CandidatePackageName = FString::Printf(
                            TEXT("%s/%s"),
                            *DestinationPath,
                            *SlotName);
                        if (FPackageName::DoesPackageExist(CandidatePackageName))
                        {
                            AuthoredMaterial =
                                LoadObject<UMaterialInterface>(nullptr, *CandidateObjectPath);
                        }
                    }

                    if (AuthoredMaterial)
                    {
                        Material = AuthoredMaterial;
                        StaticMaterial.MaterialInterface = AuthoredMaterial;
                        ++RecoveredMaterialBindings;
                    }
                    else
                    {
                        ++Failed;
                        UE_LOG(
                            LogTemp,
                            Error,
                            TEXT("ShireProductionImport authored material binding FAILED: mesh=%s slot=%s candidate=%s"),
                            *AssetName,
                            *SlotName,
                            *CandidateObjectPath);
                    }
                }

                UPackage* Package = Material ? Material->GetOutermost() : nullptr;
                if (Package && Package != GetTransientPackage())
                {
                    Package->MarkPackageDirty();
                    if (Package->GetName().StartsWith(TEXT("/Game/Production/")))
                    {
                        ImportedMaterialPackages.AddUnique(Package);
                    }
                    ++MarkedMaterialPackages;
                }
            }
            ImportedMesh->MarkPackageDirty();
        }

        // UE4.27 import factories are not perfectly consistent about which result
        // collection they populate in unattended mode. Treat the import as successful
        // when any task result is reported or the expected asset can be resolved.
        const bool bImported =
            Task->ImportedObjectPaths.Num() > 0 ||
            Task->Result.Num() > 0 ||
            ImportedAsset != nullptr;

        UE_LOG(
            LogTemp,
            Display,
            TEXT("ShireProductionImport result: %s | paths=%d result=%d resolved=%s bare-obj-materials=%s authored-material-import=%s smoothing-injected=%s tangent-generation=%s material-packages-marked=%d"),
            *Filename,
            Task->ImportedObjectPaths.Num(),
            Task->Result.Num(),
            ImportedAsset ? TEXT("yes") : TEXT("no"),
            bBareObjMaterialImportDisabled ? TEXT("disabled") : TEXT("n/a"),
            bAuthoredMaterialImportForced ? TEXT("forced") : TEXT("n/a"),
            bInjectedSmoothingGroup ? TEXT("yes") : TEXT("no"),
            bBuiltInTangentsForUntexturedObj ? TEXT("builtin-no-uv") : TEXT("default"),
            MarkedMaterialPackages);

        if (!bImported)
        {
            ++Failed;
            UE_LOG(LogTemp, Error, TEXT("ShireProductionImport FAILED: %s"), *Filename);
        }
        else
        {
            UE_LOG(LogTemp, Display, TEXT("ShireProductionImport imported: %s"), *Filename);
        }
    }

    // Sweep authored-material destination folders through AssetRegistry as a second
    // recovery path. Some UE4.27 OBJ factories register the material asset but do not
    // return it through the import task or static-mesh material pointer during the same
    // unattended import. Including in-memory assets here lets us mark and persist those
    // packages before any startup/chapter audit reloads the mesh from disk.
    if (AuthoredMaterialDestinationPaths.Num() > 0)
    {
        FAssetRegistryModule& AssetRegistryModule =
            FModuleManager::LoadModuleChecked<FAssetRegistryModule>(TEXT("AssetRegistry"));
        int32 RegistryMaterialAssets = 0;

        for (const FString& DestinationPath : AuthoredMaterialDestinationPaths)
        {
            TArray<FAssetData> Assets;
            AssetRegistryModule.Get().GetAssetsByPath(
                FName(*DestinationPath),
                Assets,
                false, // bRecursive
                false  // bIncludeOnlyOnDiskAssets
            );

            for (const FAssetData& AssetData : Assets)
            {
                if (UMaterialInterface* Material = Cast<UMaterialInterface>(AssetData.GetAsset()))
                {
                    UPackage* Package = Material->GetOutermost();
                    if (Package && Package != GetTransientPackage())
                    {
                        Package->MarkPackageDirty();
                        ImportedMaterialPackages.AddUnique(Package);
                        ++RegistryMaterialAssets;
                    }
                }
            }
        }

        UE_LOG(
            LogTemp,
            Display,
            TEXT("ShireProductionImport material registry recovery: folders=%d assets=%d bindings=%d packages=%d"),
            AuthoredMaterialDestinationPaths.Num(),
            RegistryMaterialAssets,
            RecoveredMaterialBindings,
            ImportedMaterialPackages.Num());
    }

    // OBJ import may create secondary material packages that UE4.27 does not
    // consistently include in UAssetImportTask::ImportedObjectPaths. Save those exact
    // packages explicitly before the broader dirty-package pass; on unattended UE4.27
    // the generic dirty save can report success while secondary OBJ materials remain
    // memory-only, leaving the saved meshes with broken /Game/Production references.
    if (ImportedMaterialPackages.Num() > 0)
    {
        for (UPackage* Package : ImportedMaterialPackages)
        {
            if (Package)
            {
                Package->MarkPackageDirty();
            }
        }

        SaveMaterialPackagesDeterministically(TEXT("post-mesh-binding"));

        UE_LOG(
            LogTemp,
            Display,
            TEXT("ShireProductionImport explicit material package save: %d packages"),
            ImportedMaterialPackages.Num());
    }

    // Keep the broad pass for imported meshes/textures and any other secondary assets.
    const bool bSavedDirtyPackages = FEditorFileUtils::SaveDirtyPackages(
        false,  // bPromptUserToSave
        false,  // bSaveMapPackages
        true,   // bSaveContentPackages
        true,   // bFastSave
        false,  // bNotifyNoPackagesSaved
        false); // bCanBeDeclined
    UE_LOG(
        LogTemp,
        Display,
        TEXT("ShireProductionImport secondary package save: %s"),
        bSavedDirtyPackages ? TEXT("ok") : TEXT("no-dirty-or-failed"));

    int32 MissingMaterialFiles = 0;
    for (UPackage* Package : ImportedMaterialPackages)
    {
        if (!Package || Package == GetTransientPackage())
        {
            continue;
        }

        const FString PackageFilename = FPackageName::LongPackageNameToFilename(
            Package->GetName(),
            FPackageName::GetAssetPackageExtension());

        if (!IFileManager::Get().FileExists(*PackageFilename))
        {
            ++MissingMaterialFiles;
            ++Failed;
            UE_LOG(
                LogTemp,
                Error,
                TEXT("ShireProductionImport material verification FAILED: package=%s file=%s"),
                *Package->GetName(),
                *PackageFilename);
        }
    }

    UE_LOG(
        LogTemp,
        Display,
        TEXT("ShireProductionImport material persistence verification: missing=%d tracked=%d"),
        MissingMaterialFiles,
        ImportedMaterialPackages.Num());

    UE_LOG(LogTemp, Display, TEXT("ShireProductionImport: %d files, %d failures"), SourceFiles.Num(), Failed);

    // The copy is only needed during import. Best-effort cleanup keeps Saved/
    // smaller; if interrupted, .gitignore still prevents it becoming source debt.
    IFileManager::Get().DeleteDirectory(*WorkingRoot, false, true);

    return Failed == 0 ? 0 : 3;
}
