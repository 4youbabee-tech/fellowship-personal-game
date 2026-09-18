using UnrealBuildTool;

public class ShireJourney : ModuleRules
{
    public ShireJourney(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

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
    }
}
