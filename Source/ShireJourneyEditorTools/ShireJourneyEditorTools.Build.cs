using UnrealBuildTool;

public class ShireJourneyEditorTools : ModuleRules
{
    public ShireJourneyEditorTools(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine" });
        PrivateDependencyModuleNames.AddRange(new string[]
        {
            "UnrealEd",
            "AnimGraph",
            "AnimGraphRuntime",
            "BlueprintGraph",
            "KismetCompiler",
            "AssetTools",
            "AssetRegistry",
            "ShireJourney",
            "Json",
            "JsonUtilities"
        });
    }
}
