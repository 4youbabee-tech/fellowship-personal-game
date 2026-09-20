using UnrealBuildTool;
using System;
using System.Collections.Generic;

public class ShireJourneyEditorTarget : TargetRules
{
    public ShireJourneyEditorTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Editor;
        DefaultBuildSettings = BuildSettingsVersion.V2;
        ExtraModuleNames.Add("ShireJourney");
        ExtraModuleNames.Add("ShireJourneyEditorTools");

        // CI compile/runtime validation does not need debugger symbols. The
        // self-hosted VS2019 service has intermittently failed inside c1xx with
        // D8050 while writing debug command-line records. Scope this workaround
        // to CI only so normal local Development Editor builds keep symbols.
        if (Environment.GetEnvironmentVariable("SHIRE_CI_NO_DEBUGINFO") == "1")
        {
            bDisableDebugInfo = true;
            bOmitPCDebugInfoInDevelopment = true;
            bUsePDBFiles = false;
            bUseIncrementalLinking = false;
        }
    }
}
