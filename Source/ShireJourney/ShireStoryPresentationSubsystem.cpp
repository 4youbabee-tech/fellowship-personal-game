#include "ShireStoryPresentationSubsystem.h"

#include "ShireDialogueSubsystem.h"
#include "ShireQuestSubsystem.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "TimerManager.h"

void UShireStoryPresentationSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    Collection.InitializeDependency<UShireQuestSubsystem>();
    Collection.InitializeDependency<UShireDialogueSubsystem>();
    BuildCueLibrary();

    if (UGameInstance* GI = GetGameInstance())
    {
        if (UShireQuestSubsystem* Quests = GI->GetSubsystem<UShireQuestSubsystem>())
        {
            Quests->OnStoryBeatTriggered.AddDynamic(this, &UShireStoryPresentationSubsystem::HandleStoryBeat);
        }
    }
}

void UShireStoryPresentationSubsystem::Deinitialize()
{
    if (UWorld* World = GetWorld())
    {
        World->GetTimerManager().ClearTimer(CinematicReleaseTimer);
    }

    if (UGameInstance* GI = GetGameInstance())
    {
        if (UShireQuestSubsystem* Quests = GI->GetSubsystem<UShireQuestSubsystem>())
        {
            Quests->OnStoryBeatTriggered.RemoveDynamic(this, &UShireStoryPresentationSubsystem::HandleStoryBeat);
        }
    }

    CueLibrary.Empty();
    ActiveCue = FShireStoryPresentationCue();
    bCinematicLocked = false;
    Super::Deinitialize();
}

void UShireStoryPresentationSubsystem::AddCue(FName StoryBeatId, EShireStoryPresentationMode Mode,
    FName CameraCue, FName DialogueCue, FName AmbienceCue, FName MusicCue, FName SfxCue,
    float SuggestedDuration)
{
    if (StoryBeatId == NAME_None)
    {
        return;
    }

    FShireStoryPresentationCue Cue;
    Cue.StoryBeatId = StoryBeatId;
    Cue.Mode = Mode;
    Cue.CameraCue = CameraCue;
    Cue.DialogueCue = DialogueCue;
    Cue.AmbienceCue = AmbienceCue;
    Cue.MusicCue = MusicCue;
    Cue.SfxCue = SfxCue;
    Cue.SuggestedDuration = FMath::Max(0.0f, SuggestedDuration);
    CueLibrary.Add(StoryBeatId, Cue);
}

void UShireStoryPresentationSubsystem::BuildCueLibrary()
{
    CueLibrary.Empty();

    AddCue(TEXT("BreeRoadNightfall"), EShireStoryPresentationMode::GameplayBlend,
        TEXT("Cam_BreeRoadNightfall"), NAME_None, TEXT("Amb_RainRoad"), TEXT("Mus_BreeUnease"), TEXT("Sfx_DistantHooves"), 5.0f);
    AddCue(TEXT("PrancingPonyExterior"), EShireStoryPresentationMode::GameplayBlend,
        TEXT("Cam_PonyExteriorReveal"), NAME_None, TEXT("Amb_BreeRain"), TEXT("Mus_BreeWarmThreshold"), TEXT("Sfx_InnMurmur"), 4.0f);
    AddCue(TEXT("RingIncident"), EShireStoryPresentationMode::Cinematic,
        TEXT("Cam_RingIncident"), TEXT("Dlg_BreeRingIncident"), TEXT("Amb_CommonRoomDrop"), TEXT("Mus_RingTension"), TEXT("Sfx_RingPulse"), 8.0f);
    AddCue(TEXT("StriderPrivateRoom"), EShireStoryPresentationMode::Cinematic,
        TEXT("Cam_StriderPrivateRoom"), TEXT("Dlg_StriderWarning"), TEXT("Amb_InnPrivateRoom"), TEXT("Mus_StriderMystery"), NAME_None, 12.0f);
    AddCue(TEXT("NazgulAttackPrancingPony"), EShireStoryPresentationMode::Cinematic,
        TEXT("Cam_NazgulPonyAttack"), NAME_None, TEXT("Amb_BreeNight"), TEXT("Mus_NazgulThreat"), TEXT("Sfx_BedStabs"), 10.0f);
    AddCue(TEXT("DepartBree"), EShireStoryPresentationMode::GameplayBlend,
        TEXT("Cam_DepartBree"), TEXT("Dlg_StriderDeparture"), TEXT("Amb_BreeDawn"), TEXT("Mus_RoadEast"), TEXT("Sfx_DawnBirds"), 5.0f);

    AddCue(TEXT("MidgewaterRoad"), EShireStoryPresentationMode::GameplayBlend,
        TEXT("Cam_MidgewaterWide"), NAME_None, TEXT("Amb_MarshWind"), TEXT("Mus_WildernessLow"), TEXT("Sfx_Midges"), 4.0f);
    AddCue(TEXT("WeathertopReveal"), EShireStoryPresentationMode::GameplayBlend,
        TEXT("Cam_WeathertopReveal"), NAME_None, TEXT("Amb_HighWind"), TEXT("Mus_WeathertopDread"), NAME_None, 6.0f);
    AddCue(TEXT("WeathertopCamp"), EShireStoryPresentationMode::GameplayBlend,
        TEXT("Cam_WeathertopCamp"), TEXT("Dlg_WeathertopCamp"), TEXT("Amb_NightHill"), TEXT("Mus_QuietBeforeNazgul"), TEXT("Sfx_SmallFire"), 6.0f);
    AddCue(TEXT("NazgulCloseIn"), EShireStoryPresentationMode::Cinematic,
        TEXT("Cam_NazgulCloseIn"), NAME_None, TEXT("Amb_NightHill"), TEXT("Mus_NazgulAssault"), TEXT("Sfx_BladesDrawn"), 10.0f);
    AddCue(TEXT("MorgulWound"), EShireStoryPresentationMode::Cinematic,
        TEXT("Cam_MorgulWound"), TEXT("Dlg_AfterWound"), TEXT("Amb_RingDistortion"), TEXT("Mus_WoundAftermath"), TEXT("Sfx_HeartPulse"), 10.0f);
    AddCue(TEXT("FordChase"), EShireStoryPresentationMode::Cinematic,
        TEXT("Cam_FordChase"), TEXT("Dlg_ArwenFlight"), TEXT("Amb_RiverApproach"), TEXT("Mus_FordPursuit"), TEXT("Sfx_HorseGallop"), 14.0f);
    AddCue(TEXT("FordEscape"), EShireStoryPresentationMode::Cinematic,
        TEXT("Cam_FordEscape"), NAME_None, TEXT("Amb_RiverCrash"), TEXT("Mus_RivendellRelief"), TEXT("Sfx_FloodSurge"), 10.0f);

    AddCue(TEXT("RivendellAwakening"), EShireStoryPresentationMode::Cinematic,
        TEXT("Cam_RivendellAwakening"), TEXT("Dlg_RivendellAwakening"), TEXT("Amb_RivendellWater"), TEXT("Mus_RivendellThemeOriginal"), TEXT("Sfx_SoftBirds"), 10.0f);
    AddCue(TEXT("CouncilBegins"), EShireStoryPresentationMode::Cinematic,
        TEXT("Cam_CouncilBegins"), TEXT("Dlg_CouncilOriginal"), TEXT("Amb_RivendellCourtyard"), TEXT("Mus_CouncilGravity"), NAME_None, 18.0f);
    AddCue(TEXT("FellowshipAssembled"), EShireStoryPresentationMode::Cinematic,
        TEXT("Cam_FellowshipAssembled"), TEXT("Dlg_FellowshipFormationOriginal"), TEXT("Amb_RivendellCourtyard"), TEXT("Mus_FellowshipResolveOriginal"), NAME_None, 12.0f);
    AddCue(TEXT("RivendellDeparture"), EShireStoryPresentationMode::GameplayBlend,
        TEXT("Cam_RivendellDeparture"), TEXT("Dlg_RivendellFarewell"), TEXT("Amb_RivendellMorning"), TEXT("Mus_JourneyBegins"), TEXT("Sfx_GearAndSteps"), 8.0f);

    AddCue(TEXT("FellowshipMarch"), EShireStoryPresentationMode::GameplayBlend,
        TEXT("Cam_FellowshipMarch"), TEXT("Dlg_FellowshipTravel"), TEXT("Amb_OpenCountry"), TEXT("Mus_SouthwardTravel"), NAME_None, 6.0f);
    AddCue(TEXT("CaradhrasApproach"), EShireStoryPresentationMode::GameplayBlend,
        TEXT("Cam_CaradhrasApproach"), NAME_None, TEXT("Amb_MountainWind"), TEXT("Mus_CaradhrasWarning"), TEXT("Sfx_DistantSnowFall"), 6.0f);
    AddCue(TEXT("CaradhrasStorm"), EShireStoryPresentationMode::Cinematic,
        TEXT("Cam_CaradhrasStorm"), TEXT("Dlg_CaradhrasOriginal"), TEXT("Amb_MountainStorm"), TEXT("Mus_CaradhrasCrisis"), TEXT("Sfx_Avalanche"), 14.0f);
    AddCue(TEXT("MoriaLake"), EShireStoryPresentationMode::GameplayBlend,
        TEXT("Cam_MoriaLake"), TEXT("Dlg_MoriaGateSearch"), TEXT("Amb_StillWater"), TEXT("Mus_MoriaThreshold"), TEXT("Sfx_WaterLap"), 7.0f);
    AddCue(TEXT("MoriaDoorOpens"), EShireStoryPresentationMode::Cinematic,
        TEXT("Cam_MoriaDoorOpen"), TEXT("Dlg_MoriaDoorOriginal"), TEXT("Amb_MoriaEntrance"), TEXT("Mus_EnterMoria"), TEXT("Sfx_StoneDoor"), 10.0f);

    AddCue(TEXT("MoriaEntry"), EShireStoryPresentationMode::GameplayBlend,
        TEXT("Cam_MoriaEntry"), NAME_None, TEXT("Amb_MoriaDeep"), TEXT("Mus_MoriaLow"), TEXT("Sfx_DistantDrips"), 5.0f);
    AddCue(TEXT("MoriaUnease"), EShireStoryPresentationMode::GameplayBlend,
        TEXT("Cam_MoriaUnease"), TEXT("Dlg_MoriaWhispers"), TEXT("Amb_MoriaDeep"), TEXT("Mus_MoriaUnease"), TEXT("Sfx_DistantStone"), 5.0f);
    AddCue(TEXT("BalinsTombReveal"), EShireStoryPresentationMode::Cinematic,
        TEXT("Cam_BalinsTombReveal"), TEXT("Dlg_BalinTombOriginal"), TEXT("Amb_TombStillness"), TEXT("Mus_MoriaGrief"), NAME_None, 12.0f);
    AddCue(TEXT("MoriaAttack"), EShireStoryPresentationMode::GameplayBlend,
        TEXT("Cam_MoriaAttackStart"), TEXT("Dlg_MoriaAttack"), TEXT("Amb_MoriaBattle"), TEXT("Mus_MoriaCombat"), TEXT("Sfx_DrumsDeep"), 8.0f);
    AddCue(TEXT("BalrogApproach"), EShireStoryPresentationMode::Cinematic,
        TEXT("Cam_BalrogApproach"), TEXT("Dlg_BalrogApproach"), TEXT("Amb_MoriaFireDeep"), TEXT("Mus_BalrogDread"), TEXT("Sfx_BalrogRoar"), 12.0f);
    AddCue(TEXT("BridgeConfrontation"), EShireStoryPresentationMode::Cinematic,
        TEXT("Cam_BridgeConfrontation"), TEXT("Dlg_BridgeOriginalIntent"), TEXT("Amb_BridgeChasm"), TEXT("Mus_BridgeCrisis"), TEXT("Sfx_BridgeCrack"), 16.0f);
    AddCue(TEXT("MoriaEscape"), EShireStoryPresentationMode::Cinematic,
        TEXT("Cam_MoriaEscape"), TEXT("Dlg_MoriaAftermath"), TEXT("Amb_OutsideMoria"), TEXT("Mus_GriefAfterMoria"), TEXT("Sfx_WindOutside"), 12.0f);

    AddCue(TEXT("LorienEntry"), EShireStoryPresentationMode::GameplayBlend,
        TEXT("Cam_LorienEntry"), TEXT("Dlg_LorienFirstContact"), TEXT("Amb_LorienForest"), TEXT("Mus_LorienMysteryOriginal"), TEXT("Sfx_ForestChimes"), 8.0f);
    AddCue(TEXT("LorienFarewell"), EShireStoryPresentationMode::Cinematic,
        TEXT("Cam_LorienFarewell"), TEXT("Dlg_LorienGiftsOriginal"), TEXT("Amb_LorienRiver"), TEXT("Mus_LorienFarewellOriginal"), NAME_None, 14.0f);
    AddCue(TEXT("LorienDeparture"), EShireStoryPresentationMode::GameplayBlend,
        TEXT("Cam_LorienDeparture"), NAME_None, TEXT("Amb_AnduinUpper"), TEXT("Mus_RiverJourney"), TEXT("Sfx_Paddles"), 6.0f);

    AddCue(TEXT("AnduinDeparture"), EShireStoryPresentationMode::GameplayBlend,
        TEXT("Cam_AnduinDeparture"), TEXT("Dlg_AnduinTravel"), TEXT("Amb_AnduinRiver"), TEXT("Mus_AnduinTravel"), TEXT("Sfx_Paddles"), 6.0f);
    AddCue(TEXT("ArgonathReveal"), EShireStoryPresentationMode::Cinematic,
        TEXT("Cam_ArgonathReveal"), TEXT("Dlg_ArgonathReaction"), TEXT("Amb_AnduinCliffs"), TEXT("Mus_ArgonathAweOriginal"), NAME_None, 12.0f);
    AddCue(TEXT("AmonHenArrival"), EShireStoryPresentationMode::GameplayBlend,
        TEXT("Cam_AmonHenArrival"), TEXT("Dlg_ParthGalenCamp"), TEXT("Amb_ParthGalen"), TEXT("Mus_AmonHenUnease"), NAME_None, 6.0f);
    AddCue(TEXT("UrukAttack"), EShireStoryPresentationMode::GameplayBlend,
        TEXT("Cam_UrukAttack"), TEXT("Dlg_UrukAttack"), TEXT("Amb_AmonHenBattle"), TEXT("Mus_AmonHenCombat"), TEXT("Sfx_UrukHorns"), 8.0f);
    AddCue(TEXT("BoromirFall"), EShireStoryPresentationMode::Cinematic,
        TEXT("Cam_BoromirFall"), TEXT("Dlg_BoromirFinalOriginal"), TEXT("Amb_BattleFades"), TEXT("Mus_BoromirFarewellOriginal"), NAME_None, 16.0f);
    AddCue(TEXT("FrodoSamDeparture"), EShireStoryPresentationMode::Cinematic,
        TEXT("Cam_FrodoSamDeparture"), TEXT("Dlg_FrodoSamDepartureOriginal"), TEXT("Amb_AnduinShore"), TEXT("Mus_Part1DepartureOriginal"), TEXT("Sfx_WaterQuiet"), 14.0f);
    AddCue(TEXT("Part1End"), EShireStoryPresentationMode::Cinematic,
        TEXT("Cam_Part1End"), NAME_None, TEXT("Amb_DistantWind"), TEXT("Mus_Part1EndOriginal"), NAME_None, 12.0f);
}

bool UShireStoryPresentationSubsystem::FindCue(FName StoryBeatId, FShireStoryPresentationCue& OutCue) const
{
    if (const FShireStoryPresentationCue* Cue = CueLibrary.Find(StoryBeatId))
    {
        OutCue = *Cue;
        return true;
    }

    OutCue = FShireStoryPresentationCue();
    return false;
}

void UShireStoryPresentationSubsystem::HandleStoryBeat(FName StoryBeatId)
{
    if (StoryBeatId == NAME_None)
    {
        return;
    }

    if (!FindCue(StoryBeatId, ActiveCue))
    {
        ActiveCue.StoryBeatId = StoryBeatId;
        ActiveCue.Mode = EShireStoryPresentationMode::GameplayBlend;
        ActiveCue.CameraCue = TEXT("Cam_DefaultStoryBeat");
        ActiveCue.AmbienceCue = TEXT("Amb_DefaultRegion");
    }

    if (UGameInstance* GI = GetGameInstance())
    {
        if (UShireDialogueSubsystem* Dialogue = GI->GetSubsystem<UShireDialogueSubsystem>())
        {
            if (ActiveCue.DialogueCue != NAME_None)
            {
                Dialogue->PlayDialogueCue(ActiveCue.DialogueCue);
            }
        }
    }

    if (ActiveCue.CameraCue != NAME_None)
    {
        OnCameraCueRequested.Broadcast(ActiveCue.CameraCue);
    }
    if (ActiveCue.AmbienceCue != NAME_None)
    {
        OnAmbienceCueRequested.Broadcast(ActiveCue.AmbienceCue);
    }
    if (ActiveCue.MusicCue != NAME_None)
    {
        OnMusicCueRequested.Broadcast(ActiveCue.MusicCue);
    }
    if (ActiveCue.SfxCue != NAME_None)
    {
        OnSfxCueRequested.Broadcast(ActiveCue.SfxCue);
    }

    if (ActiveCue.Mode == EShireStoryPresentationMode::Cinematic)
    {
        if (!bCinematicLocked)
        {
            bCinematicLocked = true;
            OnCinematicStateChanged.Broadcast(true);
        }

        if (UWorld* World = GetWorld())
        {
            World->GetTimerManager().ClearTimer(CinematicReleaseTimer);
            World->GetTimerManager().SetTimer(
                CinematicReleaseTimer,
                this,
                &UShireStoryPresentationSubsystem::ReleaseCinematicLock,
                FMath::Max(1.0f, ActiveCue.SuggestedDuration),
                false);
        }
    }

    OnStoryPresentationRequested.Broadcast(ActiveCue);
}

void UShireStoryPresentationSubsystem::ReleaseCinematicLock()
{
    if (UWorld* World = GetWorld())
    {
        World->GetTimerManager().ClearTimer(CinematicReleaseTimer);
    }

    if (bCinematicLocked)
    {
        bCinematicLocked = false;
        OnCinematicStateChanged.Broadcast(false);
    }
}
