#include "StoryPresentationDirector.h"

#include "ShireNPC.h"
#include "ShireQuestSubsystem.h"

#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "TimerManager.h"

AStoryPresentationDirector::AStoryPresentationDirector()
{
    PrimaryActorTick.bCanEverTick = false;
    Tags.AddUnique(TEXT("RuntimePresentationDirector"));
}

void AStoryPresentationDirector::BeginPlay()
{
    Super::BeginPlay();

    UGameInstance* GI = GetGameInstance();
    if (!GI)
    {
        return;
    }

    if (UShireStoryPresentationSubsystem* Presentation =
        GI->GetSubsystem<UShireStoryPresentationSubsystem>())
    {
        Presentation->OnStoryPresentationRequested.AddDynamic(
            this, &AStoryPresentationDirector::HandlePresentationCue);
        Presentation->OnCinematicStateChanged.AddDynamic(
            this, &AStoryPresentationDirector::HandleCinematicStateChanged);
    }

    if (UShireQuestSubsystem* Quests = GI->GetSubsystem<UShireQuestSubsystem>())
    {
        Quests->OnChapterChanged.AddDynamic(
            this, &AStoryPresentationDirector::HandleChapterChanged);
    }
}

void AStoryPresentationDirector::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (UWorld* World = GetWorld())
    {
        World->GetTimerManager().ClearTimer(ReleaseTimer);
    }

    UGameInstance* GI = GetGameInstance();
    if (GI)
    {
        if (UShireStoryPresentationSubsystem* Presentation =
            GI->GetSubsystem<UShireStoryPresentationSubsystem>())
        {
            Presentation->OnStoryPresentationRequested.RemoveDynamic(
                this, &AStoryPresentationDirector::HandlePresentationCue);
            Presentation->OnCinematicStateChanged.RemoveDynamic(
                this, &AStoryPresentationDirector::HandleCinematicStateChanged);
        }

        if (UShireQuestSubsystem* Quests = GI->GetSubsystem<UShireQuestSubsystem>())
        {
            Quests->OnChapterChanged.RemoveDynamic(
                this, &AStoryPresentationDirector::HandleChapterChanged);
        }
    }

    ReleaseCamera();
    Super::EndPlay(EndPlayReason);
}

AStoryPresentationDirector::FShotProfile
AStoryPresentationDirector::ResolveShotProfile(const FShireStoryPresentationCue& Cue) const
{
    FShotProfile Profile;
    const FString Beat = Cue.StoryBeatId.ToString();
    const FString Camera = Cue.CameraCue.ToString();

    if (Cue.Mode == EShireStoryPresentationMode::Cinematic)
    {
        Profile.BackDistance = 360.0f;
        Profile.SideDistance = 145.0f;
        Profile.Height = 135.0f;
        Profile.FocusDistance = 420.0f;
        Profile.FocusHeight = 72.0f;
        Profile.Fov = 62.0f;
        Profile.HoldSeconds = 2.25f;
        Profile.BlendIn = 0.34f;
        Profile.BlendOut = 0.42f;
    }

    const bool bGeography =
        Camera.Contains(TEXT("Reveal"), ESearchCase::IgnoreCase) ||
        Camera.Contains(TEXT("Opening"), ESearchCase::IgnoreCase) ||
        Camera.Contains(TEXT("Departure"), ESearchCase::IgnoreCase) ||
        Camera.Contains(TEXT("Approach"), ESearchCase::IgnoreCase) ||
        Camera.Contains(TEXT("Arrival"), ESearchCase::IgnoreCase) ||
        Camera.Contains(TEXT("Wide"), ESearchCase::IgnoreCase) ||
        Beat == TEXT("ArgonathReveal") ||
        Beat == TEXT("WeathertopReveal");

    if (bGeography)
    {
        Profile.BackDistance = 540.0f;
        Profile.SideDistance = 170.0f;
        Profile.Height = 260.0f;
        Profile.FocusDistance = 980.0f;
        Profile.FocusHeight = 110.0f;
        Profile.Fov = 78.0f;
        Profile.HoldSeconds = Cue.Mode == EShireStoryPresentationMode::Cinematic ? 2.35f : 1.55f;
    }

    auto PreferSubject = [&Profile](const TCHAR* Name, float Fov = 58.0f)
    {
        Profile.bPreferNamedSubject = true;
        Profile.SubjectName = FName(Name);
        Profile.BackDistance = 285.0f;
        Profile.SideDistance = 125.0f;
        Profile.Height = 115.0f;
        Profile.FocusDistance = 0.0f;
        Profile.FocusHeight = 54.0f;
        Profile.Fov = Fov;
        Profile.HoldSeconds = 2.20f;
    };

    if (Beat == TEXT("BilboDisappearance") || Beat == TEXT("BilboReunion"))
    {
        PreferSubject(TEXT("Bilbo"), 60.0f);
    }
    else if (Beat == TEXT("StriderPrivateRoom"))
    {
        PreferSubject(TEXT("Aragorn"), 58.0f);
    }
    else if (Beat == TEXT("CouncilBegins"))
    {
        PreferSubject(TEXT("Elrond"), 61.0f);
    }
    else if (Beat == TEXT("BridgeConfrontation"))
    {
        PreferSubject(TEXT("Gandalf"), 57.0f);
    }
    else if (Beat == TEXT("Mirror") || Beat == TEXT("LorienFarewell"))
    {
        PreferSubject(TEXT("Galadriel"), 59.0f);
    }
    else if (Beat == TEXT("BoromirPressure") ||
             Beat == TEXT("BoromirDefense") ||
             Beat == TEXT("BoromirFall"))
    {
        PreferSubject(TEXT("Boromir"), Beat == TEXT("BoromirFall") ? 54.0f : 60.0f);
    }
    else if (Beat == TEXT("FrodoSamDeparture"))
    {
        PreferSubject(TEXT("Sam"), 57.0f);
    }

    // The runtime accent is a bridge until authored Level Sequences exist. It must
    // never hold the player longer than the existing 3.5 s presentation safety gate.
    Profile.HoldSeconds = FMath::Clamp(Profile.HoldSeconds, 0.65f, 2.60f);
    return Profile;
}

AActor* AStoryPresentationDirector::ResolveNamedSubject(FName SubjectName) const
{
    if (!GetWorld() || SubjectName == NAME_None)
    {
        return nullptr;
    }

    AActor* Best = nullptr;
    float BestDistanceSq = TNumericLimits<float>::Max();

    APlayerController* PC = GetWorld()->GetFirstPlayerController();
    APawn* PlayerPawn = PC ? PC->GetPawn() : nullptr;

    for (TActorIterator<AShireNPC> It(GetWorld()); It; ++It)
    {
        AShireNPC* NPC = *It;
        if (!NPC || !NPC->DisplayName.ToString().Equals(
            SubjectName.ToString(), ESearchCase::IgnoreCase))
        {
            continue;
        }

        const float DistanceSq = PlayerPawn
            ? FVector::DistSquared(PlayerPawn->GetActorLocation(), NPC->GetActorLocation())
            : 0.0f;
        if (DistanceSq < BestDistanceSq)
        {
            BestDistanceSq = DistanceSq;
            Best = NPC;
        }
    }

    return Best;
}

FVector AStoryPresentationDirector::ResolveSafeCameraLocation(
    const FVector& DesiredLocation,
    const FVector& FocusLocation,
    AActor* FocusActor,
    APawn* PlayerPawn) const
{
    UWorld* World = GetWorld();
    if (!World)
    {
        return DesiredLocation;
    }

    FCollisionQueryParams Params(SCENE_QUERY_STAT(StoryPresentationCamera), false);
    if (FocusActor)
    {
        Params.AddIgnoredActor(FocusActor);
    }
    if (PlayerPawn)
    {
        Params.AddIgnoredActor(PlayerPawn);
    }

    FHitResult Hit;
    if (World->LineTraceSingleByChannel(
        Hit,
        FocusLocation,
        DesiredLocation,
        ECC_Visibility,
        Params))
    {
        return Hit.Location + Hit.ImpactNormal * 45.0f;
    }

    return DesiredLocation;
}

void AStoryPresentationDirector::HandlePresentationCue(FShireStoryPresentationCue Cue)
{
    if (!GetWorld() || Cue.Mode == EShireStoryPresentationMode::Gameplay)
    {
        return;
    }

    APlayerController* PC = GetWorld()->GetFirstPlayerController();
    APawn* PlayerPawn = PC ? PC->GetPawn() : nullptr;
    if (!PC || !PlayerPawn)
    {
        return;
    }

    // Never steal control from an authored camera/Level Sequence. The runtime accent
    // only owns the ordinary player view or its own previous transient camera.
    AActor* CurrentViewTarget = PC->GetViewTarget();
    if (CurrentViewTarget && CurrentViewTarget != PlayerPawn && CurrentViewTarget != RuntimeCamera)
    {
        return;
    }

    ReleaseCamera();

    const FShotProfile Profile = ResolveShotProfile(Cue);
    AActor* Subject = Profile.bPreferNamedSubject
        ? ResolveNamedSubject(Profile.SubjectName)
        : nullptr;

    const FVector BasisLocation = Subject
        ? Subject->GetActorLocation()
        : PlayerPawn->GetActorLocation();
    const FRotator BasisRotation = Subject
        ? Subject->GetActorRotation()
        : PlayerPawn->GetActorRotation();

    const FVector Forward = BasisRotation.Vector().GetSafeNormal();
    const FVector Right = FRotationMatrix(BasisRotation).GetScaledAxis(EAxis::Y).GetSafeNormal();

    FVector FocusLocation = BasisLocation + FVector(0, 0, Profile.FocusHeight);
    if (!Subject)
    {
        FocusLocation += Forward * Profile.FocusDistance;
    }

    const float SideSign = (GetTypeHash(Cue.StoryBeatId) & 1u) ? 1.0f : -1.0f;
    FVector DesiredLocation =
        BasisLocation -
        Forward * Profile.BackDistance +
        Right * (Profile.SideDistance * SideSign) +
        FVector(0, 0, Profile.Height);

    DesiredLocation = ResolveSafeCameraLocation(
        DesiredLocation,
        FocusLocation,
        Subject,
        PlayerPawn);

    FActorSpawnParameters SpawnParams;
    SpawnParams.SpawnCollisionHandlingOverride =
        ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

    RuntimeCamera = GetWorld()->SpawnActor<ACameraActor>(
        DesiredLocation,
        (FocusLocation - DesiredLocation).Rotation(),
        SpawnParams);
    if (!RuntimeCamera)
    {
        return;
    }

    RuntimeCamera->Tags.AddUnique(TEXT("RuntimePresentationGenerated"));
    if (UCameraComponent* CameraComponent = RuntimeCamera->GetCameraComponent())
    {
        CameraComponent->SetFieldOfView(Profile.Fov);
    }

    PreviousViewTarget = PlayerPawn;
    PC->SetViewTargetWithBlend(
        RuntimeCamera,
        Profile.BlendIn,
        EViewTargetBlendFunction::VTBlend_Cubic,
        0.0f,
        true);

    GetWorld()->GetTimerManager().SetTimer(
        ReleaseTimer,
        this,
        &AStoryPresentationDirector::ReleaseCamera,
        Profile.HoldSeconds,
        false);

    UE_LOG(
        LogTemp,
        Display,
        TEXT("StoryPresentation: beat=%s camera=%s subject=%s fov=%.1f hold=%.2f"),
        *Cue.StoryBeatId.ToString(),
        *Cue.CameraCue.ToString(),
        Subject ? *Profile.SubjectName.ToString() : TEXT("GEOGRAPHY"),
        Profile.Fov,
        Profile.HoldSeconds);
}

void AStoryPresentationDirector::HandleChapterChanged(FName PreviousChapterId, FName NewChapterId)
{
    if (UGameInstance* GI = GetGameInstance())
    {
        if (UShireStoryPresentationSubsystem* Presentation =
            GI->GetSubsystem<UShireStoryPresentationSubsystem>())
        {
            Presentation->ReleaseCinematicLock();
        }
    }
    ReleaseCamera();
}

void AStoryPresentationDirector::HandleCinematicStateChanged(bool bLocked)
{
    if (!bLocked)
    {
        ReleaseCamera();
    }
}

void AStoryPresentationDirector::ReleaseCamera()
{
    UWorld* World = GetWorld();
    if (World)
    {
        World->GetTimerManager().ClearTimer(ReleaseTimer);
    }

    APlayerController* PC = World ? World->GetFirstPlayerController() : nullptr;
    AActor* ReturnTarget = PreviousViewTarget.Get();
    if (PC && RuntimeCamera && PC->GetViewTarget() == RuntimeCamera && ReturnTarget)
    {
        PC->SetViewTargetWithBlend(
            ReturnTarget,
            0.34f,
            EViewTargetBlendFunction::VTBlend_Cubic,
            0.0f,
            true);
    }

    if (RuntimeCamera)
    {
        RuntimeCamera->Destroy();
        RuntimeCamera = nullptr;
    }
    PreviousViewTarget.Reset();
}
