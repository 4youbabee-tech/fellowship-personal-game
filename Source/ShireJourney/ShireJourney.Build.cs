using UnrealBuildTool;
using System.IO;

public class ShireJourney : ModuleRules
{
    public ShireJourney(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        // Physical Public/Private migration completed in CP-W00-152.
        // Keep existing basename includes stable without exporting the module root:
        // only intentional public domain headers are visible to this and dependent modules.
        PublicIncludePaths.AddRange(new string[]
        {
            Path.Combine(ModuleDirectory, "Public", "Core"),
            Path.Combine(ModuleDirectory, "Public", "Characters"),
            Path.Combine(ModuleDirectory, "Public", "World"),
            Path.Combine(ModuleDirectory, "Public", "Subsystems"),
            Path.Combine(ModuleDirectory, "Public", "UI"),
            Path.Combine(ModuleDirectory, "Public", "SaveGame"),
            Path.Combine(ModuleDirectory, "Public", "Prototypes")
        });

        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "InputCore",
            "Json",
            "JsonUtilities"
        });

        RuntimeDependencies.Add("$(ProjectDir)/Data/NPCSocialModel.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/NPCConversationPlan.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/NPCMemoryPlan.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/BoundedDialoguePlan.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/LivingWorldEventPlan.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/CharacterMotionPlan.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/ChapterAtmospherePlan.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/WorldDressingPlan.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/ResourceIntegrationPlan.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/WorldLifeSaturationPlan.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/WorldResourceFloodPlan.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/WorldResourceBankCP54.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/WorldActivityMovementPlan.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/FellowshipExperienceMegaPassCP56.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/LivingNPCIntelligencePlan.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/NPCRegionalMoodPlan.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/FilmDialogueSourceContext.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/ExplorationEnvelopePlan.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/JourneyDiscoveryRewardPlan.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/ContextualSideActivityPlan.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/TrilogyRingQuestPlan.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/ModernGameLayerPlan.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/PlayerLifeProgressionPlan.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/ChronicleMapKnowledgePlan.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/Part1ProductionAtlas.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/Part1WorldMap.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/Part1VisualProductionPass.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/MegaMaterialWorldWaveV1.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/RealmDetailSaturationV2.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/CinematicPerformancePlanV3.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/Part1SonicWorldPlan.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/HeroCharacterEquipmentSilhouetteV4.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/ChapterAssetStreamingPlan.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/AssetPerformanceBudget.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/EnsembleFilmMissionPlan.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/FilmSideContentMasterPlan.json", StagedFileType.NonUFS);
        RuntimeDependencies.Add("$(ProjectDir)/Data/SideContentCanonCatalog.json", StagedFileType.NonUFS);
    }
}
