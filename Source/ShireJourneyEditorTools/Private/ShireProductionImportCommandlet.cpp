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
#include "StaticMeshResources.h"
#include "Engine/Texture2D.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformFilemanager.h"
#include "Misc/FileHelper.h"
#include "Misc/PackageName.h"
#include "Misc/Paths.h"
#include "Materials/Material.h"
#include "Materials/MaterialExpressionScalarParameter.h"
#include "Materials/MaterialExpressionTextureSampleParameter2D.h"
#include "Materials/MaterialExpressionMultiply.h"
#include "Materials/MaterialExpressionMaterialFunctionCall.h"
#include "Materials/MaterialFunction.h"
#include "Materials/MaterialExpressionVectorParameter.h"
#include "Materials/MaterialInterface.h"
#include "Materials/MaterialInstanceConstant.h"
#include "Modules/ModuleManager.h"
#include "UObject/Package.h"
#include "UObject/UObjectGlobals.h"

namespace ShireProductionImport
{
    static bool IsApprovedFoliageMaterialIdentity(const FString& AuthoredMaterialName)
    {
        const FString NormalizedIdentity = AuthoredMaterialName.TrimStartAndEnd();
        return NormalizedIdentity.Equals(TEXT("Grass"), ESearchCase::CaseSensitive) ||
            NormalizedIdentity.Equals(TEXT("Leaves"), ESearchCase::CaseSensitive) ||
            NormalizedIdentity.Equals(TEXT("LeafGreen"), ESearchCase::CaseSensitive) ||
            NormalizedIdentity.Equals(TEXT("LeafGold"), ESearchCase::CaseSensitive);
    }

    static bool IsP1C01FoliageMeshAssetName(const FString& AssetName)
    {
        return AssetName.Equals(TEXT("SM_ShGrassClump"), ESearchCase::CaseSensitive) ||
            AssetName.Equals(TEXT("SM_ShHedge"), ESearchCase::CaseSensitive) ||
            AssetName.Equals(TEXT("SM_ShShrub"), ESearchCase::CaseSensitive) ||
            AssetName.Equals(TEXT("SM_ShTreeCanopy"), ESearchCase::CaseSensitive) ||
            AssetName.Equals(TEXT("SM_ShTreeTrunk"), ESearchCase::CaseSensitive);
    }

    static bool HasObjTextureCoordinates(const FString& ObjSource)
    {
        return ObjSource.StartsWith(TEXT("vt ")) ||
            ObjSource.Contains(TEXT("\nvt "), ESearchCase::CaseSensitive);
    }

    static bool ParseObjVertex(const FString& Line, FVector& OutVertex)
    {
        TArray<FString> Parts;
        Line.ParseIntoArrayWS(Parts);
        if (Parts.Num() < 4 || Parts[0] != TEXT("v"))
        {
            return false;
        }

        OutVertex.X = FCString::Atof(*Parts[1]);
        OutVertex.Y = FCString::Atof(*Parts[2]);
        OutVertex.Z = FCString::Atof(*Parts[3]);
        return FMath::IsFinite(OutVertex.X) &&
            FMath::IsFinite(OutVertex.Y) &&
            FMath::IsFinite(OutVertex.Z);
    }

    static bool ParseObjFaceVertex(
        const FString& Token,
        int32 VertexCount,
        int32& OutVertexIndex,
        FString& OutNormalSuffix)
    {
        FString VertexText = Token;
        OutNormalSuffix.Empty();

        const int32 SlashIndex = Token.Find(TEXT("/"));
        if (SlashIndex != INDEX_NONE)
        {
            VertexText = Token.Left(SlashIndex);
            const FString Remainder = Token.Mid(SlashIndex + 1);
            if (!Remainder.IsEmpty())
            {
                if (!Remainder.StartsWith(TEXT("/")))
                {
                    return false;
                }
                OutNormalSuffix = Remainder;
            }
        }

        const int32 RawIndex = FCString::Atoi(*VertexText);
        if (RawIndex == 0)
        {
            return false;
        }

        const int32 ResolvedIndex =
            RawIndex > 0 ? RawIndex - 1 : VertexCount + RawIndex;
        if (ResolvedIndex < 0 || ResolvedIndex >= VertexCount)
        {
            return false;
        }

        OutVertexIndex = ResolvedIndex;
        return true;
    }

    static bool InjectDeterministicFaceUVs(
        FString& ObjSource,
        bool& bOutInjected)
    {
        bOutInjected = false;
        if (HasObjTextureCoordinates(ObjSource))
        {
            return true;
        }

        TArray<FString> Lines;
        ObjSource.ParseIntoArrayLines(Lines, false);

        TArray<FVector> Vertices;
        Vertices.Reserve(Lines.Num());
        for (const FString& RawLine : Lines)
        {
            const FString Line = RawLine.TrimStartAndEnd();
            if (!Line.StartsWith(TEXT("v ")))
            {
                continue;
            }

            FVector Vertex = FVector::ZeroVector;
            if (!ParseObjVertex(Line, Vertex))
            {
                return false;
            }
            Vertices.Add(Vertex);
        }

        if (Vertices.Num() < 3)
        {
            return true;
        }

        FVector MinBounds = Vertices[0];
        FVector MaxBounds = Vertices[0];
        for (const FVector& Vertex : Vertices)
        {
            MinBounds.X = FMath::Min(MinBounds.X, Vertex.X);
            MinBounds.Y = FMath::Min(MinBounds.Y, Vertex.Y);
            MinBounds.Z = FMath::Min(MinBounds.Z, Vertex.Z);
            MaxBounds.X = FMath::Max(MaxBounds.X, Vertex.X);
            MaxBounds.Y = FMath::Max(MaxBounds.Y, Vertex.Y);
            MaxBounds.Z = FMath::Max(MaxBounds.Z, Vertex.Z);
        }

        TArray<FString> GeneratedUVLines;
        int32 NextUVIndex = 1;
        int32 FirstFaceLine = INDEX_NONE;

        for (int32 LineIndex = 0; LineIndex < Lines.Num(); ++LineIndex)
        {
            const FString Trimmed = Lines[LineIndex].TrimStartAndEnd();
            if (!Trimmed.StartsWith(TEXT("f ")))
            {
                continue;
            }

            if (FirstFaceLine == INDEX_NONE)
            {
                FirstFaceLine = LineIndex;
            }

            TArray<FString> Tokens;
            Trimmed.Mid(2).ParseIntoArrayWS(Tokens);
            if (Tokens.Num() < 3)
            {
                return false;
            }

            TArray<int32> FaceVertexIndices;
            TArray<FString> FaceNormalSuffixes;
            FaceVertexIndices.Reserve(Tokens.Num());
            FaceNormalSuffixes.Reserve(Tokens.Num());

            for (const FString& Token : Tokens)
            {
                int32 VertexIndex = INDEX_NONE;
                FString NormalSuffix;
                if (!ParseObjFaceVertex(
                        Token,
                        Vertices.Num(),
                        VertexIndex,
                        NormalSuffix))
                {
                    return false;
                }
                FaceVertexIndices.Add(VertexIndex);
                FaceNormalSuffixes.Add(NormalSuffix);
            }

            FVector FaceNormal = FVector::ZeroVector;
            const FVector Base = Vertices[FaceVertexIndices[0]];
            for (int32 Corner = 1; Corner + 1 < FaceVertexIndices.Num(); ++Corner)
            {
                const FVector A = Vertices[FaceVertexIndices[Corner]] - Base;
                const FVector B = Vertices[FaceVertexIndices[Corner + 1]] - Base;
                FaceNormal = FVector::CrossProduct(A, B);
                if (FaceNormal.SizeSquared() > KINDA_SMALL_NUMBER)
                {
                    break;
                }
            }

            if (FaceNormal.SizeSquared() <= KINDA_SMALL_NUMBER)
            {
                return false;
            }

            const FVector AbsNormal(
                FMath::Abs(FaceNormal.X),
                FMath::Abs(FaceNormal.Y),
                FMath::Abs(FaceNormal.Z));

            int32 AxisU = 0;
            int32 AxisV = 1;
            if (AbsNormal.X >= AbsNormal.Y && AbsNormal.X >= AbsNormal.Z)
            {
                AxisU = 1;
                AxisV = 2;
            }
            else if (AbsNormal.Y >= AbsNormal.X && AbsNormal.Y >= AbsNormal.Z)
            {
                AxisU = 0;
                AxisV = 2;
            }

            const auto AxisValue = [](const FVector& Value, int32 Axis)
            {
                return Axis == 0 ? Value.X : (Axis == 1 ? Value.Y : Value.Z);
            };

            const float MinU = AxisValue(MinBounds, AxisU);
            const float MaxU = AxisValue(MaxBounds, AxisU);
            const float MinV = AxisValue(MinBounds, AxisV);
            const float MaxV = AxisValue(MaxBounds, AxisV);
            const float RangeU = MaxU - MinU;
            const float RangeV = MaxV - MinV;
            if (FMath::Abs(RangeU) <= KINDA_SMALL_NUMBER ||
                FMath::Abs(RangeV) <= KINDA_SMALL_NUMBER)
            {
                return false;
            }

            TArray<FString> RewrittenTokens;
            RewrittenTokens.Reserve(Tokens.Num());
            for (int32 Corner = 0; Corner < FaceVertexIndices.Num(); ++Corner)
            {
                const int32 VertexIndex = FaceVertexIndices[Corner];
                const FVector& Vertex = Vertices[VertexIndex];
                const float U = FMath::Clamp(
                    (AxisValue(Vertex, AxisU) - MinU) / RangeU,
                    0.0f,
                    1.0f);
                const float V = FMath::Clamp(
                    (AxisValue(Vertex, AxisV) - MinV) / RangeV,
                    0.0f,
                    1.0f);

                GeneratedUVLines.Add(FString::Printf(
                    TEXT("vt %.6f %.6f"),
                    U,
                    V));

                const FString& NormalSuffix = FaceNormalSuffixes[Corner];
                const int32 SourceVertexIndex = VertexIndex + 1;
                RewrittenTokens.Add(NormalSuffix.IsEmpty()
                    ? FString::Printf(
                        TEXT("%d/%d"),
                        SourceVertexIndex,
                        NextUVIndex)
                    : FString::Printf(
                        TEXT("%d/%d%s"),
                        SourceVertexIndex,
                        NextUVIndex,
                        *NormalSuffix));
                ++NextUVIndex;
            }

            Lines[LineIndex] =
                FString(TEXT("f ")) + FString::Join(RewrittenTokens, TEXT(" "));
        }

        if (GeneratedUVLines.Num() == 0 || FirstFaceLine == INDEX_NONE)
        {
            return true;
        }

        TArray<FString> OutputLines;
        OutputLines.Reserve(Lines.Num() + GeneratedUVLines.Num());
        for (int32 LineIndex = 0; LineIndex < Lines.Num(); ++LineIndex)
        {
            if (LineIndex == FirstFaceLine)
            {
                OutputLines.Append(GeneratedUVLines);
            }
            OutputLines.Add(Lines[LineIndex]);
        }

        ObjSource = FString::Join(OutputLines, TEXT("\n")) + TEXT("\n");
        bOutInjected = true;
        return true;
    }
}

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
    TArray<FString> StaticFbxFiles;
    TArray<FString> CharacterFbxFiles;
    TArray<FString> MaterialLibraryFiles;
    IFileManager::Get().FindFilesRecursive(TextureFiles, *WorkingRoot, TEXT("*.png"), true, false, false);
    IFileManager::Get().FindFilesRecursive(TextureFiles, *WorkingRoot, TEXT("*.tga"), true, false, false);
    IFileManager::Get().FindFilesRecursive(MeshFiles, *WorkingRoot, TEXT("*.obj"), true, false, false);
    TArray<FString> AllFbxFiles;
    IFileManager::Get().FindFilesRecursive(AllFbxFiles, *WorkingRoot, TEXT("*.fbx"), true, false, false);
    for (const FString& FbxFile : AllFbxFiles)
    {
        FString RelativeFbx = FbxFile;
        FPaths::MakePathRelativeTo(RelativeFbx, *(WorkingRoot / TEXT("")));
        RelativeFbx.ReplaceInline(TEXT("\\"), TEXT("/"));
        if (RelativeFbx.StartsWith(TEXT("Characters/Rigs/"), ESearchCase::IgnoreCase))
        {
            CharacterFbxFiles.Add(FbxFile);
        }
        else
        {
            StaticFbxFiles.Add(FbxFile);
        }
    }
    IFileManager::Get().FindFilesRecursive(MaterialLibraryFiles, *WorkingRoot, TEXT("*.mtl"), true, false, false);
    TextureFiles.Sort();
    MeshFiles.Sort();
    StaticFbxFiles.Sort();
    CharacterFbxFiles.Sort();
    MaterialLibraryFiles.Sort();
    SourceFiles.Append(TextureFiles);
    SourceFiles.Append(MeshFiles);
    SourceFiles.Append(StaticFbxFiles);

    if (SourceFiles.Num() == 0 && CharacterFbxFiles.Num() == 0)
    {
        UE_LOG(LogTemp, Warning, TEXT("ShireProductionImport: no production assets found at %s"), *SourceRoot);
        return 0;
    }

    UE_LOG(
        LogTemp,
        Display,
        TEXT("ShireProductionImport source inventory: textures=%d objStatic=%d fbxStatic=%d fbxCharacterQcOnly=%d"),
        TextureFiles.Num(),
        MeshFiles.Num(),
        StaticFbxFiles.Num(),
        CharacterFbxFiles.Num());

    for (const FString& CharacterFbx : CharacterFbxFiles)
    {
        UE_LOG(
            LogTemp,
            Display,
            TEXT("ShireProductionImport character FBX deferred to skeletal QC lane: %s"),
            *CharacterFbx);
    }

    FAssetToolsModule& AssetTools = FModuleManager::LoadModuleChecked<FAssetToolsModule>(TEXT("AssetTools"));
    int32 Failed = 0;
    TArray<UPackage*> ImportedMaterialPackages;

    struct FPendingAlbedoBinding
    {
        FString MaterialObjectPath;
        FString TextureObjectPath;
    };
    TArray<FPendingAlbedoBinding> PendingAlbedoBindings;

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
        FindObject<UMaterialInterface>(nullptr, ProductionSurfacePath);
    if (!ProductionMaterialParent)
    {
        const FString ProductionSurfaceObjectPath(ProductionSurfacePath);
        const FString ProductionSurfacePackage =
            FPackageName::ObjectPathToPackageName(ProductionSurfaceObjectPath);
        if (FPackageName::DoesPackageExist(ProductionSurfacePackage))
        {
            ProductionMaterialParent =
                LoadObject<UMaterialInterface>(nullptr, ProductionSurfacePath);
        }
    }

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
            ColorParameter->DefaultValue = FLinearColor::White;
            SurfaceMaterial->Expressions.Add(ColorParameter);

            UMaterialExpressionTextureSampleParameter2D* AlbedoParameter =
                NewObject<UMaterialExpressionTextureSampleParameter2D>(SurfaceMaterial);
            AlbedoParameter->ParameterName = TEXT("AlbedoTexture");
            AlbedoParameter->Texture = LoadObject<UTexture2D>(
                nullptr,
                TEXT("/Engine/EngineResources/WhiteSquareTexture.WhiteSquareTexture"));
            SurfaceMaterial->Expressions.Add(AlbedoParameter);

            UMaterialExpressionMultiply* BaseColorMultiply =
                NewObject<UMaterialExpressionMultiply>(SurfaceMaterial);
            BaseColorMultiply->A.Expression = AlbedoParameter;
            BaseColorMultiply->B.Expression = ColorParameter;
            SurfaceMaterial->Expressions.Add(BaseColorMultiply);
            SurfaceMaterial->BaseColor.Expression = BaseColorMultiply;

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

            UMaterialExpressionScalarParameter* SpecularParameter =
                NewObject<UMaterialExpressionScalarParameter>(SurfaceMaterial);
            SpecularParameter->ParameterName = TEXT("Specular");
            SpecularParameter->DefaultValue = 0.32f;
            SurfaceMaterial->Expressions.Add(SpecularParameter);
            SurfaceMaterial->Specular.Expression = SpecularParameter;

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

    // D: create a deterministic texture-free water master. Runtime residency is
    // owned by the chapter bank; this editor-only creation path does not authorize
    // planar reflections, scene captures, WPO, translucency or CPU water simulation.
    const TCHAR* ProductionWaterPath =
        TEXT("/Game/Production/Materials/M_ProductionWater.M_ProductionWater");
    UMaterialInterface* ProductionWaterMaterial =
        FindObject<UMaterialInterface>(nullptr, ProductionWaterPath);
    if (!ProductionWaterMaterial)
    {
        const FString ProductionWaterObjectPath(ProductionWaterPath);
        const FString ProductionWaterPackage =
            FPackageName::ObjectPathToPackageName(ProductionWaterObjectPath);
        if (FPackageName::DoesPackageExist(ProductionWaterPackage))
        {
            ProductionWaterMaterial =
                LoadObject<UMaterialInterface>(nullptr, ProductionWaterPath);
        }
    }

    if (!ProductionWaterMaterial)
    {
        UMaterialFactoryNew* WaterFactory = NewObject<UMaterialFactoryNew>();
        UMaterial* WaterMaterial = Cast<UMaterial>(
            AssetTools.Get().CreateAsset(
                TEXT("M_ProductionWater"),
                TEXT("/Game/Production/Materials"),
                UMaterial::StaticClass(),
                WaterFactory));

        if (WaterMaterial)
        {
            UMaterialExpressionVectorParameter* WaterColorParameter =
                NewObject<UMaterialExpressionVectorParameter>(WaterMaterial);
            WaterColorParameter->ParameterName = TEXT("WaterColor");
            WaterColorParameter->DefaultValue = FLinearColor(0.035f, 0.17f, 0.24f, 1.0f);
            WaterMaterial->Expressions.Add(WaterColorParameter);
            WaterMaterial->BaseColor.Expression = WaterColorParameter;

            UMaterialExpressionScalarParameter* WaterRoughnessParameter =
                NewObject<UMaterialExpressionScalarParameter>(WaterMaterial);
            WaterRoughnessParameter->ParameterName = TEXT("Roughness");
            WaterRoughnessParameter->DefaultValue = 0.22f;
            WaterMaterial->Expressions.Add(WaterRoughnessParameter);
            WaterMaterial->Roughness.Expression = WaterRoughnessParameter;

            UMaterialExpressionScalarParameter* WaterMetallicParameter =
                NewObject<UMaterialExpressionScalarParameter>(WaterMaterial);
            WaterMetallicParameter->ParameterName = TEXT("Metallic");
            WaterMetallicParameter->DefaultValue = 0.0f;
            WaterMaterial->Expressions.Add(WaterMetallicParameter);
            WaterMaterial->Metallic.Expression = WaterMetallicParameter;

            UMaterialExpressionScalarParameter* WaterSpecularParameter =
                NewObject<UMaterialExpressionScalarParameter>(WaterMaterial);
            WaterSpecularParameter->ParameterName = TEXT("Specular");
            WaterSpecularParameter->DefaultValue = 0.62f;
            WaterMaterial->Expressions.Add(WaterSpecularParameter);
            WaterMaterial->Specular.Expression = WaterSpecularParameter;

            WaterMaterial->PostEditChange();
            WaterMaterial->MarkPackageDirty();
            ImportedMaterialPackages.AddUnique(WaterMaterial->GetOutermost());
            ProductionWaterMaterial = WaterMaterial;
            UE_LOG(
                LogTemp,
                Display,
                TEXT("D_WATER_MATERIAL_EVIDENCE created M_ProductionWater opaque=yes textureSamples=0 wpo=no sceneCapture=no"));
        }
        else
        {
            ++Failed;
            UE_LOG(
                LogTemp,
                Error,
                TEXT("ShireProductionImport failed to create M_ProductionWater master material."));
        }
    }

    // Drop C2: create a dedicated foliage master without assigning it yet.
    // Grass/leaves will be re-parented in C3 by stable authored material identity.
    // SimpleGrassWind executes in the material vertex path, so there is no per-tree
    // Actor Tick. Distance complexity is reduced by assigning the separate no-WPO
    // far master in C3/C4, rather than adding another unsupported expression here.
    const TCHAR* ProductionFoliagePath =
        TEXT("/Game/Production/Materials/M_ProductionFoliage.M_ProductionFoliage");
    UMaterialInterface* ProductionFoliageParent =
        FindObject<UMaterialInterface>(nullptr, ProductionFoliagePath);
    if (!ProductionFoliageParent)
    {
        const FString ProductionFoliageObjectPath(ProductionFoliagePath);
        const FString ProductionFoliagePackage =
            FPackageName::ObjectPathToPackageName(ProductionFoliageObjectPath);
        if (FPackageName::DoesPackageExist(ProductionFoliagePackage))
        {
            ProductionFoliageParent =
                LoadObject<UMaterialInterface>(nullptr, ProductionFoliagePath);
        }
    }

    if (!ProductionFoliageParent)
    {
        UMaterialFactoryNew* FoliageFactory = NewObject<UMaterialFactoryNew>();
        UMaterial* FoliageMaterial = Cast<UMaterial>(
            AssetTools.Get().CreateAsset(
                TEXT("M_ProductionFoliage"),
                TEXT("/Game/Production/Materials"),
                UMaterial::StaticClass(),
                FoliageFactory));

        if (FoliageMaterial)
        {
            FoliageMaterial->TwoSided = true;

            UMaterialExpressionVectorParameter* FoliageColorParameter =
                NewObject<UMaterialExpressionVectorParameter>(FoliageMaterial);
            FoliageColorParameter->ParameterName = TEXT("Color");
            FoliageColorParameter->DefaultValue = FLinearColor::White;
            FoliageMaterial->Expressions.Add(FoliageColorParameter);

            UMaterialExpressionTextureSampleParameter2D* FoliageAlbedoParameter =
                NewObject<UMaterialExpressionTextureSampleParameter2D>(FoliageMaterial);
            FoliageAlbedoParameter->ParameterName = TEXT("AlbedoTexture");
            FoliageAlbedoParameter->Texture = LoadObject<UTexture2D>(
                nullptr,
                TEXT("/Engine/EngineResources/WhiteSquareTexture.WhiteSquareTexture"));
            FoliageMaterial->Expressions.Add(FoliageAlbedoParameter);

            UMaterialExpressionMultiply* FoliageBaseColorMultiply =
                NewObject<UMaterialExpressionMultiply>(FoliageMaterial);
            FoliageBaseColorMultiply->A.Expression = FoliageAlbedoParameter;
            FoliageBaseColorMultiply->B.Expression = FoliageColorParameter;
            FoliageMaterial->Expressions.Add(FoliageBaseColorMultiply);
            FoliageMaterial->BaseColor.Expression = FoliageBaseColorMultiply;

            UMaterialExpressionScalarParameter* FoliageRoughnessParameter =
                NewObject<UMaterialExpressionScalarParameter>(FoliageMaterial);
            FoliageRoughnessParameter->ParameterName = TEXT("Roughness");
            FoliageRoughnessParameter->DefaultValue = 0.78f;
            FoliageMaterial->Expressions.Add(FoliageRoughnessParameter);
            FoliageMaterial->Roughness.Expression = FoliageRoughnessParameter;

            UMaterialExpressionScalarParameter* FoliageMetallicParameter =
                NewObject<UMaterialExpressionScalarParameter>(FoliageMaterial);
            FoliageMetallicParameter->ParameterName = TEXT("Metallic");
            FoliageMetallicParameter->DefaultValue = 0.0f;
            FoliageMaterial->Expressions.Add(FoliageMetallicParameter);
            FoliageMaterial->Metallic.Expression = FoliageMetallicParameter;

            UMaterialExpressionScalarParameter* FoliageSpecularParameter =
                NewObject<UMaterialExpressionScalarParameter>(FoliageMaterial);
            FoliageSpecularParameter->ParameterName = TEXT("Specular");
            FoliageSpecularParameter->DefaultValue = 0.20f;
            FoliageMaterial->Expressions.Add(FoliageSpecularParameter);
            FoliageMaterial->Specular.Expression = FoliageSpecularParameter;

            UMaterialExpressionScalarParameter* WindIntensityParameter =
                NewObject<UMaterialExpressionScalarParameter>(FoliageMaterial);
            WindIntensityParameter->ParameterName = TEXT("WindIntensity");
            WindIntensityParameter->DefaultValue = 0.18f;
            FoliageMaterial->Expressions.Add(WindIntensityParameter);

            UMaterialExpressionScalarParameter* WindSpeedParameter =
                NewObject<UMaterialExpressionScalarParameter>(FoliageMaterial);
            WindSpeedParameter->ParameterName = TEXT("WindSpeed");
            WindSpeedParameter->DefaultValue = 0.28f;
            FoliageMaterial->Expressions.Add(WindSpeedParameter);

            UMaterialExpressionScalarParameter* WindWeightParameter =
                NewObject<UMaterialExpressionScalarParameter>(FoliageMaterial);
            WindWeightParameter->ParameterName = TEXT("WindWeight");
            WindWeightParameter->DefaultValue = 1.0f;
            FoliageMaterial->Expressions.Add(WindWeightParameter);

            UMaterialFunction* SimpleGrassWindFunction =
                LoadObject<UMaterialFunction>(
                    nullptr,
                    TEXT("/Engine/Functions/Engine_MaterialFunctions01/WorldPositionOffset/SimpleGrassWind.SimpleGrassWind"));

            UMaterialExpressionMaterialFunctionCall* SimpleWind =
                NewObject<UMaterialExpressionMaterialFunctionCall>(FoliageMaterial);

            bool bSimpleWindBound = false;
            if (SimpleGrassWindFunction && SimpleWind)
            {
                SimpleWind->MaterialFunction = SimpleGrassWindFunction;
                SimpleWind->UpdateFromFunctionResource();

                // UE4.27 SimpleGrassWind exposes inputs in documented order:
                // WindIntensity, WindWeight, WindSpeed, AdditionalWPO.
                FExpressionInput* WindIntensityInput = SimpleWind->GetInput(0);
                FExpressionInput* WindWeightInput = SimpleWind->GetInput(1);
                FExpressionInput* WindSpeedInput = SimpleWind->GetInput(2);

                if (WindIntensityInput && WindWeightInput && WindSpeedInput)
                {
                    WindIntensityInput->Expression = WindIntensityParameter;
                    WindWeightInput->Expression = WindWeightParameter;
                    WindSpeedInput->Expression = WindSpeedParameter;

                    FoliageMaterial->Expressions.Add(SimpleWind);
                    FoliageMaterial->WorldPositionOffset.Expression = SimpleWind;
                    bSimpleWindBound = true;
                }
            }

            if (!bSimpleWindBound)
            {
                ++Failed;
                UE_LOG(
                    LogTemp,
                    Error,
                    TEXT("ShireProductionImport failed to bind UE4.27 SimpleGrassWind material function."));
            }

            FoliageMaterial->PostEditChange();
            FoliageMaterial->MarkPackageDirty();
            ImportedMaterialPackages.AddUnique(FoliageMaterial->GetOutermost());
            ProductionFoliageParent = FoliageMaterial;
            UE_LOG(
                LogTemp,
                Display,
                TEXT("ShireProductionImport created M_ProductionFoliage master material with parameterized SimpleGrassWind."));
        }
        else
        {
            ++Failed;
            UE_LOG(
                LogTemp,
                Error,
                TEXT("ShireProductionImport failed to create M_ProductionFoliage master material."));
        }
    }


    // Far foliage uses a separate no-WPO master. C3/C4 will bind this to distant
    // LOD material slots so far vegetation removes wind vertex instructions entirely.
    const TCHAR* ProductionFoliageFarPath =
        TEXT("/Game/Production/Materials/M_ProductionFoliageFar.M_ProductionFoliageFar");
    UMaterialInterface* ProductionFoliageFarParent =
        FindObject<UMaterialInterface>(nullptr, ProductionFoliageFarPath);
    if (!ProductionFoliageFarParent)
    {
        const FString ProductionFoliageFarObjectPath(ProductionFoliageFarPath);
        const FString ProductionFoliageFarPackage =
            FPackageName::ObjectPathToPackageName(ProductionFoliageFarObjectPath);
        if (FPackageName::DoesPackageExist(ProductionFoliageFarPackage))
        {
            ProductionFoliageFarParent =
                LoadObject<UMaterialInterface>(nullptr, ProductionFoliageFarPath);
        }
    }

    if (!ProductionFoliageFarParent)
    {
        UMaterialFactoryNew* FoliageFarFactory = NewObject<UMaterialFactoryNew>();
        UMaterial* FoliageFarMaterial = Cast<UMaterial>(
            AssetTools.Get().CreateAsset(
                TEXT("M_ProductionFoliageFar"),
                TEXT("/Game/Production/Materials"),
                UMaterial::StaticClass(),
                FoliageFarFactory));

        if (FoliageFarMaterial)
        {
            FoliageFarMaterial->TwoSided = true;

            UMaterialExpressionVectorParameter* FoliageFarColorParameter =
                NewObject<UMaterialExpressionVectorParameter>(FoliageFarMaterial);
            FoliageFarColorParameter->ParameterName = TEXT("Color");
            FoliageFarColorParameter->DefaultValue = FLinearColor::White;
            FoliageFarMaterial->Expressions.Add(FoliageFarColorParameter);

            UMaterialExpressionTextureSampleParameter2D* FoliageFarAlbedoParameter =
                NewObject<UMaterialExpressionTextureSampleParameter2D>(FoliageFarMaterial);
            FoliageFarAlbedoParameter->ParameterName = TEXT("AlbedoTexture");
            FoliageFarAlbedoParameter->Texture = LoadObject<UTexture2D>(
                nullptr,
                TEXT("/Engine/EngineResources/WhiteSquareTexture.WhiteSquareTexture"));
            FoliageFarMaterial->Expressions.Add(FoliageFarAlbedoParameter);

            UMaterialExpressionMultiply* FoliageFarBaseColorMultiply =
                NewObject<UMaterialExpressionMultiply>(FoliageFarMaterial);
            FoliageFarBaseColorMultiply->A.Expression = FoliageFarAlbedoParameter;
            FoliageFarBaseColorMultiply->B.Expression = FoliageFarColorParameter;
            FoliageFarMaterial->Expressions.Add(FoliageFarBaseColorMultiply);
            FoliageFarMaterial->BaseColor.Expression = FoliageFarBaseColorMultiply;

            UMaterialExpressionScalarParameter* FoliageFarRoughnessParameter =
                NewObject<UMaterialExpressionScalarParameter>(FoliageFarMaterial);
            FoliageFarRoughnessParameter->ParameterName = TEXT("Roughness");
            FoliageFarRoughnessParameter->DefaultValue = 0.78f;
            FoliageFarMaterial->Expressions.Add(FoliageFarRoughnessParameter);
            FoliageFarMaterial->Roughness.Expression = FoliageFarRoughnessParameter;

            UMaterialExpressionScalarParameter* FoliageFarMetallicParameter =
                NewObject<UMaterialExpressionScalarParameter>(FoliageFarMaterial);
            FoliageFarMetallicParameter->ParameterName = TEXT("Metallic");
            FoliageFarMetallicParameter->DefaultValue = 0.0f;
            FoliageFarMaterial->Expressions.Add(FoliageFarMetallicParameter);
            FoliageFarMaterial->Metallic.Expression = FoliageFarMetallicParameter;

            UMaterialExpressionScalarParameter* FoliageFarSpecularParameter =
                NewObject<UMaterialExpressionScalarParameter>(FoliageFarMaterial);
            FoliageFarSpecularParameter->ParameterName = TEXT("Specular");
            FoliageFarSpecularParameter->DefaultValue = 0.20f;
            FoliageFarMaterial->Expressions.Add(FoliageFarSpecularParameter);
            FoliageFarMaterial->Specular.Expression = FoliageFarSpecularParameter;

            FoliageFarMaterial->PostEditChange();
            FoliageFarMaterial->MarkPackageDirty();
            ImportedMaterialPackages.AddUnique(FoliageFarMaterial->GetOutermost());
            ProductionFoliageFarParent = FoliageFarMaterial;
            UE_LOG(
                LogTemp,
                Display,
                TEXT("ShireProductionImport created M_ProductionFoliageFar no-WPO master."));
        }
        else
        {
            ++Failed;
            UE_LOG(
                LogTemp,
                Error,
                TEXT("ShireProductionImport failed to create M_ProductionFoliageFar master material."));
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
            FString CurrentAlbedoMap;
            FLinearColor CurrentBaseColor(0.35f, 0.35f, 0.35f, 1.0f);
            float CurrentRoughness = 0.68f;
            float CurrentMetallic = 0.0f;
            float CurrentSpecular = 0.32f;

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

                const bool bApprovedFoliageIdentity =
                    ShireProductionImport::IsApprovedFoliageMaterialIdentity(CurrentMaterialName);
                UMaterialInterface* DesiredMaterialParent = ProductionMaterialParent;
                if (bApprovedFoliageIdentity)
                {
                    if (!ProductionFoliageParent)
                    {
                        ++Failed;
                        UE_LOG(
                            LogTemp,
                            Error,
                            TEXT("ShireProductionImport: approved foliage material %s cannot bind because M_ProductionFoliage is unavailable."),
                            *CurrentMaterialName);
                        return;
                    }
                    DesiredMaterialParent = ProductionFoliageParent;
                }

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
                    Factory->InitialParent = DesiredMaterialParent;
                    Instance = Cast<UMaterialInstanceConstant>(
                        AssetTools.Get().CreateAsset(
                            CurrentMaterialName,
                            DestinationPath,
                            UMaterialInstanceConstant::StaticClass(),
                            Factory));
                }

                if (Instance)
                {
                    Instance->SetParentEditorOnly(DesiredMaterialParent);
                    Instance->SetVectorParameterValueEditorOnly(
                        FMaterialParameterInfo(TEXT("Color")),
                        CurrentBaseColor);
                    Instance->SetScalarParameterValueEditorOnly(
                        FMaterialParameterInfo(TEXT("Roughness")),
                        FMath::Clamp(CurrentRoughness, 0.0f, 1.0f));
                    Instance->SetScalarParameterValueEditorOnly(
                        FMaterialParameterInfo(TEXT("Metallic")),
                        FMath::Clamp(CurrentMetallic, 0.0f, 1.0f));
                    Instance->SetScalarParameterValueEditorOnly(
                        FMaterialParameterInfo(TEXT("Specular")),
                        FMath::Clamp(CurrentSpecular, 0.0f, 1.0f));

                    if (!CurrentAlbedoMap.IsEmpty())
                    {
                        FString AlbedoSourcePath = FPaths::ConvertRelativePathToFull(
                            FPaths::Combine(FPaths::GetPath(MtlFilename), CurrentAlbedoMap));
                        FPaths::NormalizeFilename(AlbedoSourcePath);

                        FString RelativeTexturePath = AlbedoSourcePath;
                        FPaths::MakePathRelativeTo(RelativeTexturePath, *(WorkingRoot / TEXT("")));
                        RelativeTexturePath.ReplaceInline(TEXT("\\"), TEXT("/"));

                        const FString RelativeTextureDir = FPaths::GetPath(RelativeTexturePath);
                        const FString TextureAssetName = FPaths::GetBaseFilename(RelativeTexturePath);
                        const FString TextureDestinationPath = RelativeTextureDir.IsEmpty()
                            ? TEXT("/Game/Production")
                            : FString::Printf(TEXT("/Game/Production/%s"), *RelativeTextureDir);
                        const FString TextureObjectPath = FString::Printf(
                            TEXT("%s/%s.%s"),
                            *TextureDestinationPath,
                            *TextureAssetName,
                            *TextureAssetName);

                        PendingAlbedoBindings.Add({
                            ObjectPath,
                            TextureObjectPath
                        });
                    }

                    UE_LOG(
                        LogTemp,
                        Display,
                        TEXT("ShireProductionImport material response: identity=%s parent=%s foliage=%s roughness=%.3f metallic=%.3f specular=%.3f albedo=%s"),
                        *CurrentMaterialName,
                        *DesiredMaterialParent->GetPathName(),
                        bApprovedFoliageIdentity ? TEXT("yes") : TEXT("no"),
                        CurrentRoughness,
                        CurrentMetallic,
                        CurrentSpecular,
                        CurrentAlbedoMap.IsEmpty() ? TEXT("none") : *CurrentAlbedoMap);

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
                    CurrentAlbedoMap.Empty();
                    CurrentBaseColor = FLinearColor(0.35f, 0.35f, 0.35f, 1.0f);
                    CurrentRoughness = 0.68f;
                    CurrentMetallic = 0.0f;
                    CurrentSpecular = 0.32f;
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
                else if (Line.StartsWith(TEXT("Ks "), ESearchCase::IgnoreCase) &&
                    !CurrentMaterialName.IsEmpty())
                {
                    TArray<FString> Parts;
                    Line.ParseIntoArrayWS(Parts);
                    if (Parts.Num() >= 4)
                    {
                        const float KsR = FCString::Atof(*Parts[1]);
                        const float KsG = FCString::Atof(*Parts[2]);
                        const float KsB = FCString::Atof(*Parts[3]);
                        CurrentSpecular = FMath::Clamp((KsR + KsG + KsB) / 3.0f * 4.0f, 0.02f, 0.65f);
                    }
                }
                else if (Line.StartsWith(TEXT("map_Kd "), ESearchCase::IgnoreCase) &&
                    !CurrentMaterialName.IsEmpty())
                {
                    CurrentAlbedoMap = Line.Mid(7).TrimStartAndEnd();
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
    int32 GeneratedUVSourceMeshes = 0;

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
        bool bInjectedGeneratedUVs = false;
        bool bAuthoredMaterialImportForced = false;
        bool bBuiltInTangentsForUntexturedObj = false;
        TArray<FString> AuthoredMaterialNames;
        const FString SourceExtension = FPaths::GetExtension(Filename).ToLower();
        if (SourceExtension == TEXT("fbx"))
        {
            UFbxImportUI* ImportOptions = NewObject<UFbxImportUI>();
            ImportOptions->MeshTypeToImport = EFBXImportType::FBXIT_StaticMesh;
            ImportOptions->bImportAsSkeletal = false;
            ImportOptions->bImportAnimations = false;
            ImportOptions->bImportMaterials = false;
            ImportOptions->bImportTextures = false;
            if (ImportOptions->StaticMeshImportData)
            {
                ImportOptions->StaticMeshImportData->bRemoveDegenerates = true;
                ImportOptions->StaticMeshImportData->NormalImportMethod = EFBXNormalImportMethod::FBXNIM_ImportNormalsAndTangents;
            }
            Task->Options = ImportOptions;
            UE_LOG(LogTemp, Display, TEXT("ShireProductionImport static FBX enabled: %s -> %s"), *Filename, *DestinationPath);
        }
        else if (SourceExtension == TEXT("obj"))
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

                if (!ShireProductionImport::InjectDeterministicFaceUVs(
                        ObjSource,
                        bInjectedGeneratedUVs))
                {
                    ++Failed;
                    UE_LOG(
                        LogTemp,
                        Error,
                        TEXT("ShireProductionImport: deterministic UV normalization failed file=%s"),
                        *Filename);
                    continue;
                }
                if (bInjectedGeneratedUVs)
                {
                    if (!FFileHelper::SaveStringToFile(ObjSource, *Filename))
                    {
                        ++Failed;
                        UE_LOG(
                            LogTemp,
                            Error,
                            TEXT("ShireProductionImport: failed to persist generated UV working copy file=%s"),
                            *Filename);
                        continue;
                    }
                    ++GeneratedUVSourceMeshes;
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
                        ShireProductionImport::HasObjTextureCoordinates(ObjSource);

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
                if (Package &&
                    Package != GetTransientPackage() &&
                    Package->GetName().StartsWith(TEXT("/Game/Production/")))
                {
                    // Never dirty Engine/Plugin packages referenced as fallback materials.
                    // The one-click importer owns only project production content.
                    Package->MarkPackageDirty();
                    ImportedMaterialPackages.AddUnique(Package);
                    ++MarkedMaterialPackages;
                }
            }
            if (ShireProductionImport::IsP1C01FoliageMeshAssetName(AssetName))
            {
                const FStaticMeshRenderData* RenderData = ImportedMesh->GetRenderData();
                if (!RenderData || RenderData->LODResources.Num() == 0)
                {
                    ++Failed;
                    UE_LOG(
                        LogTemp,
                        Error,
                        TEXT("C4_FOLIAGE_EVIDENCE_FAILED mesh=%s reason=no-render-lod-data"),
                        *ExpectedObjectPath);
                }
                else
                {
                    const int32 LodCount = RenderData->LODResources.Num();
                    for (int32 LodIndex = 0; LodIndex < LodCount; ++LodIndex)
                    {
                        const FStaticMeshLODResources& LodResources =
                            RenderData->LODResources[LodIndex];

                        if (LodResources.Sections.Num() == 0)
                        {
                            UE_LOG(
                                LogTemp,
                                Display,
                                TEXT("C4_FOLIAGE_EVIDENCE mesh=%s lodCount=%d lod=%d section=-1 materialIndex=-1 materialIdentity=NONE parent=NONE proposedParent=NONE decision=NO_SECTION reason=empty-lod-section-list"),
                                *ExpectedObjectPath,
                                LodCount,
                                LodIndex);
                            continue;
                        }

                        for (int32 SectionIndex = 0;
                             SectionIndex < LodResources.Sections.Num();
                             ++SectionIndex)
                        {
                            const FStaticMeshSection& Section =
                                LodResources.Sections[SectionIndex];
                            const int32 MaterialIndex = Section.MaterialIndex;

                            FString MaterialIdentity = TEXT("NONE");
                            FString CurrentParentPath = TEXT("NONE");
                            bool bApprovedFoliageMaterial = false;

                            if (StaticMaterials.IsValidIndex(MaterialIndex))
                            {
                                const FStaticMaterial& SectionMaterial =
                                    StaticMaterials[MaterialIndex];
                                MaterialIdentity =
                                    SectionMaterial.MaterialSlotName.IsNone()
                                        ? TEXT("NONE")
                                        : SectionMaterial.MaterialSlotName.ToString();

                                bApprovedFoliageMaterial =
                                    ShireProductionImport::IsApprovedFoliageMaterialIdentity(
                                        MaterialIdentity);

                                if (const UMaterialInstanceConstant* MaterialInstance =
                                    Cast<UMaterialInstanceConstant>(
                                        SectionMaterial.MaterialInterface))
                                {
                                    if (MaterialInstance->Parent)
                                    {
                                        CurrentParentPath =
                                            MaterialInstance->Parent->GetPathName();
                                    }
                                }
                                else if (SectionMaterial.MaterialInterface)
                                {
                                    CurrentParentPath =
                                        SectionMaterial.MaterialInterface->GetPathName();
                                }
                            }

                            const bool bVerifiedFarLod =
                                LodIndex > 0 && bApprovedFoliageMaterial;
                            const TCHAR* Decision =
                                bVerifiedFarLod
                                    ? TEXT("FAR_LOD_ELIGIBLE_FOR_REVIEW")
                                    : (LodIndex == 0
                                        ? TEXT("KEEP_NEAR_MID")
                                        : TEXT("NO_FOLIAGE_PARENT_CHANGE"));
                            const TCHAR* ProposedParent =
                                bVerifiedFarLod
                                    ? ProductionFoliageFarPath
                                    : TEXT("NONE");

                            UE_LOG(
                                LogTemp,
                                Display,
                                TEXT("C4_FOLIAGE_EVIDENCE mesh=%s lodCount=%d lod=%d section=%d materialIndex=%d materialIdentity=%s parent=%s proposedParent=%s decision=%s reason=%s"),
                                *ExpectedObjectPath,
                                LodCount,
                                LodIndex,
                                SectionIndex,
                                MaterialIndex,
                                *MaterialIdentity,
                                *CurrentParentPath,
                                ProposedParent,
                                Decision,
                                bVerifiedFarLod
                                    ? TEXT("actual-far-lod-and-approved-foliage-identity")
                                    : (LodIndex == 0
                                        ? TEXT("base-lod-preserved")
                                        : TEXT("far-lod-is-not-approved-foliage-material")));
                        }
                    }
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
            TEXT("ShireProductionImport result: %s | paths=%d result=%d resolved=%s bare-obj-materials=%s authored-material-import=%s smoothing-injected=%s generated-uvs=%s tangent-generation=%s material-packages-marked=%d"),
            *Filename,
            Task->ImportedObjectPaths.Num(),
            Task->Result.Num(),
            ImportedAsset ? TEXT("yes") : TEXT("no"),
            bBareObjMaterialImportDisabled ? TEXT("disabled") : TEXT("n/a"),
            bAuthoredMaterialImportForced ? TEXT("forced") : TEXT("n/a"),
            bInjectedSmoothingGroup ? TEXT("yes") : TEXT("no"),
            bInjectedGeneratedUVs ? TEXT("yes") : TEXT("no"),
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

    int32 BoundAlbedoTextures = 0;
    int32 MissingAlbedoTextures = 0;
    for (const FPendingAlbedoBinding& Binding : PendingAlbedoBindings)
    {
        UMaterialInstanceConstant* Instance =
            FindObject<UMaterialInstanceConstant>(nullptr, *Binding.MaterialObjectPath);
        if (!Instance)
        {
            Instance = LoadObject<UMaterialInstanceConstant>(
                nullptr,
                *Binding.MaterialObjectPath);
        }

        UTexture2D* Texture =
            FindObject<UTexture2D>(nullptr, *Binding.TextureObjectPath);
        if (!Texture)
        {
            Texture = LoadObject<UTexture2D>(
                nullptr,
                *Binding.TextureObjectPath);
        }

        if (Instance && Texture)
        {
            Instance->SetTextureParameterValueEditorOnly(
                FMaterialParameterInfo(TEXT("AlbedoTexture")),
                Texture);
            Instance->PostEditChange();
            Instance->MarkPackageDirty();
            ImportedMaterialPackages.AddUnique(Instance->GetOutermost());
            ++BoundAlbedoTextures;
        }
        else
        {
            ++MissingAlbedoTextures;
            ++Failed;
            UE_LOG(
                LogTemp,
                Error,
                TEXT("ShireProductionImport albedo binding FAILED: material=%s texture=%s material-found=%s texture-found=%s"),
                *Binding.MaterialObjectPath,
                *Binding.TextureObjectPath,
                Instance ? TEXT("yes") : TEXT("no"),
                Texture ? TEXT("yes") : TEXT("no"));
        }
    }

    UE_LOG(
        LogTemp,
        Display,
        TEXT("ShireProductionImport albedo texture bindings: requested=%d bound=%d missing=%d"),
        PendingAlbedoBindings.Num(),
        BoundAlbedoTextures,
        MissingAlbedoTextures);

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
                    if (Package &&
                        Package != GetTransientPackage() &&
                        Package->GetName().StartsWith(TEXT("/Game/Production/")))
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
        TEXT("ShireProductionImport UV normalization: generated=%d"),
        GeneratedUVSourceMeshes);

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
