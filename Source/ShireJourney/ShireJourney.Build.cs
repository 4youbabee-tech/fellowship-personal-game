using UnrealBuildTool;

public class ShireJourney : ModuleRules
{
    public ShireJourney(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        // Transitional export for the currently flat guarded runtime layout.
        // Cross-module editor QA needs runtime public contracts (for example ShireSaveGame.h)
        // until the dedicated Public/Private migration moves headers under Public/<Domain>.
        PublicIncludePaths.Add(ModuleDirectory);

        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "InputCore",
            "Json",
            "JsonUtilities"
        });

        RuntimeDependencies.Add("$(ProjectDir)/Data/NPCSocialModel.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/NPCConversationPlan.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/NPCMemoryPlan.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/BoundedDialoguePlan.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/LivingWorldEventPlan.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/CharacterMotionPlan.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/ChapterAtmospherePlan.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/WorldDressingPlan.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/ResourceIntegrationPlan.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/WorldLifeSaturationPlan.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/WorldResourceFloodPlan.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/WorldResourceBankCP54.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/WorldActivityMovementPlan.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/FellowshipExperienceMegaPassCP56.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/LivingNPCIntelligencePlan.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/NPCRegionalMoodPlan.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/FilmDialogueSourceContext.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/ExplorationEnvelopePlan.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/JourneyDiscoveryRewardPlan.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/ContextualSideActivityPlan.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/TrilogyRingQuestPlan.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/ModernGameLayerPlan.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/PlayerLifeProgressionPlan.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/ChronicleMapKnowledgePlan.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/Part1ProductionAtlas.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/Part1WorldMap.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/Part1VisualProductionPass.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/MegaMaterialWorldWaveV1.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/RealmDetailSaturationV2.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/CinematicPerformancePlanV3.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/Part1SonicWorldPlan.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/HeroCharacterEquipmentSilhouetteV4.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/ChapterAssetStreamingPlan.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/AssetPerformanceBudget.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/EnsembleFilmMissionPlan.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/FilmSideContentMasterPlan.json");
        RuntimeDependencies.Add("$(ProjectDir)/Data/SideContentCanonCatalog.json");
    }
}
