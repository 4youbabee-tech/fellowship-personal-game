using UnrealBuildTool;

public class ShireJourneyEditorTools : ModuleRules
{
    public ShireJourneyEditorTools(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine" });
        PrivateDependencyModuleNames.AddRange(new string[] { "UnrealEd", "AssetTools", "AssetRegistry" });
    }
}
