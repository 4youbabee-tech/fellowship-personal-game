using UnrealBuildTool;
using System;
using System.Collections.Generic;

public class ShireJourneyTarget : TargetRules
{
    public ShireJourneyTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.V2;
        ExtraModuleNames.Add("ShireJourney");

        if (Environment.GetEnvironmentVariable("SHIRE_CI_NO_DEBUGINFO") == "1")
        {
            WindowsPlatform.bUseBundledDbgHelp = false;
        }
    }
}
