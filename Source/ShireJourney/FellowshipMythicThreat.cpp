#include "FellowshipMythicThreat.h"

#include "ShireQuestSubsystem.h"

#include "Components/PointLightComponent.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/GameInstance.h"
#include "Engine/StaticMesh.h"
#include "GameFramework/Pawn.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"

AFellowshipMythicThreat::AFellowshipMythicThreat()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.TickInterval = 0.08f;

    Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    SetRootComponent(Root);

    Core = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Core"));
    Head = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Head"));
    AppendageA = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("AppendageA"));
    AppendageB = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("AppendageB"));
    AppendageC = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("AppendageC"));
    AppendageD = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("AppendageD"));

    UStaticMeshComponent* Pieces[] = {
        Core, Head, AppendageA, AppendageB, AppendageC, AppendageD
    };
    for (UStaticMeshComponent* Piece : Pieces)
    {
        Piece->SetupAttachment(Root);
        Piece->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        Piece->SetGenerateOverlapEvents(false);
        Piece->CastShadow = true;
    }

    ThreatLight = CreateDefaultSubobject<UPointLightComponent>(TEXT("ThreatLight"));
    ThreatLight->SetupAttachment(Root);
    ThreatLight->SetIntensity(0.0f);
    ThreatLight->SetAttenuationRadius(1350.0f);
    ThreatLight->SetLightColor(FLinearColor(1.0f, 0.16f, 0.035f));

    Tags.AddUnique(TEXT("RuntimePrototypeGenerated"));
    Tags.AddUnique(TEXT("FilmLockedThreat"));
    SetActorEnableCollision(false);
}

void AFellowshipMythicThreat::ConfigureThreat(
    EFellowshipMythicThreatType InType,
    FName InActivationStoryBeat,
    FName InDeactivationStoryBeat)
{
    ThreatType = InType;
    ActivationStoryBeat = InActivationStoryBeat;
    DeactivationStoryBeat = InDeactivationStoryBeat;
    ApplyVisualProfile();
    UpdateActivation();
}

void AFellowshipMythicThreat::BeginPlay()
{
    Super::BeginPlay();
    ApplyVisualProfile();
    UpdateActivation();
}

void AFellowshipMythicThreat::SetThreatActive(bool bActive)
{
    if (bThreatActive == bActive)
    {
        return;
    }

    bThreatActive = bActive;
    SetActorHiddenInGame(!bThreatActive);
    PrimaryActorTick.SetTickFunctionEnable(true);
    PrimaryActorTick.TickInterval = bThreatActive ? 0.06f : 0.25f;
    ThreatLight->SetVisibility(bThreatActive && ThreatType == EFellowshipMythicThreatType::Balrog);

    UE_LOG(
        LogTemp,
        Display,
        TEXT("MythicThreat: type=%s active=%s activation=%s deactivation=%s storyEffect=NONE"),
        ThreatType == EFellowshipMythicThreatType::Watcher ? TEXT("Watcher") : TEXT("Balrog"),
        bThreatActive ? TEXT("yes") : TEXT("no"),
        *ActivationStoryBeat.ToString(),
        *DeactivationStoryBeat.ToString());
}

void AFellowshipMythicThreat::UpdateActivation()
{
    UGameInstance* GI = GetGameInstance();
    UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    if (!Quests)
    {
        SetThreatActive(false);
        return;
    }

    const bool bActivated =
        ActivationStoryBeat == NAME_None ||
        Quests->HasStoryBeatTriggered(ActivationStoryBeat);
    const bool bDeactivated =
        DeactivationStoryBeat != NAME_None &&
        Quests->HasStoryBeatTriggered(DeactivationStoryBeat);

    SetThreatActive(bActivated && !bDeactivated);
}

void AFellowshipMythicThreat::ApplyVisualProfile()
{
    auto TryMesh = [](UStaticMeshComponent* Component, const TCHAR* AssetPath) -> bool
    {
        if (!Component)
        {
            return false;
        }
        if (UStaticMesh* Mesh = LoadObject<UStaticMesh>(nullptr, AssetPath))
        {
            Component->SetStaticMesh(Mesh);
            return true;
        }
        return false;
    };

    UStaticMesh* Cube = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
    UStaticMesh* Sphere = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Sphere.Sphere"));
    UStaticMesh* Cylinder = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));

    UStaticMeshComponent* Pieces[] = {
        Core, Head, AppendageA, AppendageB, AppendageC, AppendageD
    };
    for (UStaticMeshComponent* Piece : Pieces)
    {
        Piece->SetVisibility(true, true);
        Piece->SetRelativeLocation(FVector::ZeroVector);
        Piece->SetRelativeRotation(FRotator::ZeroRotator);
        Piece->SetRelativeScale3D(FVector(1.0f));
    }

    bool bProductionFoundation = false;
    if (ThreatType == EFellowshipMythicThreatType::Watcher)
    {
        bProductionFoundation =
            TryMesh(Core, TEXT("/Game/Production/Enemies/Watcher/SM_Watcher_Core.SM_Watcher_Core")) &&
            TryMesh(AppendageA, TEXT("/Game/Production/Enemies/Watcher/SM_Watcher_Tentacle.SM_Watcher_Tentacle"));
        TryMesh(AppendageB, TEXT("/Game/Production/Enemies/Watcher/SM_Watcher_Tentacle.SM_Watcher_Tentacle"));
        TryMesh(AppendageC, TEXT("/Game/Production/Enemies/Watcher/SM_Watcher_Tentacle.SM_Watcher_Tentacle"));
        TryMesh(AppendageD, TEXT("/Game/Production/Enemies/Watcher/SM_Watcher_Tentacle.SM_Watcher_Tentacle"));

        if (!bProductionFoundation)
        {
            Core->SetStaticMesh(Sphere);
            AppendageA->SetStaticMesh(Cylinder);
            AppendageB->SetStaticMesh(Cylinder);
            AppendageC->SetStaticMesh(Cylinder);
            AppendageD->SetStaticMesh(Cylinder);
        }

        Head->SetVisibility(false, true);
        Core->SetRelativeLocation(FVector(0.0f, 0.0f, -35.0f));
        Core->SetRelativeScale3D(bProductionFoundation ? FVector(1.0f) : FVector(1.35f, 1.05f, 0.65f));

        const FVector TentacleOffsets[] = {
            FVector(40.0f, -155.0f, 25.0f),
            FVector(70.0f, 155.0f, 20.0f),
            FVector(-95.0f, -85.0f, 15.0f),
            FVector(-120.0f, 95.0f, 10.0f)
        };
        UStaticMeshComponent* Tentacles[] = { AppendageA, AppendageB, AppendageC, AppendageD };
        for (int32 Index = 0; Index < 4; ++Index)
        {
            Tentacles[Index]->SetRelativeLocation(TentacleOffsets[Index]);
            Tentacles[Index]->SetRelativeRotation(FRotator(0.0f, Index * 75.0f - 50.0f, -70.0f));
            Tentacles[Index]->SetRelativeScale3D(
                bProductionFoundation
                    ? FVector(0.80f + Index * 0.07f)
                    : FVector(0.16f, 0.16f, 2.6f + Index * 0.25f));
        }

        ThreatLight->SetIntensity(0.0f);
        ThreatLight->SetVisibility(false);
    }
    else
    {
        bProductionFoundation =
            TryMesh(Core, TEXT("/Game/Production/Enemies/Balrog/SM_Balrog_Torso.SM_Balrog_Torso")) &&
            TryMesh(Head, TEXT("/Game/Production/Enemies/Balrog/SM_Balrog_Head.SM_Balrog_Head"));
        TryMesh(AppendageA, TEXT("/Game/Production/Enemies/Balrog/SM_Balrog_Wing.SM_Balrog_Wing"));
        TryMesh(AppendageB, TEXT("/Game/Production/Enemies/Balrog/SM_Balrog_Wing.SM_Balrog_Wing"));
        TryMesh(AppendageC, TEXT("/Game/Production/Enemies/Balrog/SM_Balrog_Horn.SM_Balrog_Horn"));
        TryMesh(AppendageD, TEXT("/Game/Production/Enemies/Balrog/SM_Balrog_Horn.SM_Balrog_Horn"));

        if (!bProductionFoundation)
        {
            Core->SetStaticMesh(Cube);
            Head->SetStaticMesh(Sphere);
            AppendageA->SetStaticMesh(Cube);
            AppendageB->SetStaticMesh(Cube);
            AppendageC->SetStaticMesh(Cylinder);
            AppendageD->SetStaticMesh(Cylinder);
        }

        Core->SetRelativeLocation(FVector(0.0f, 0.0f, 170.0f));
        Head->SetRelativeLocation(FVector(35.0f, 0.0f, 425.0f));
        AppendageA->SetRelativeLocation(FVector(-30.0f, -155.0f, 260.0f));
        AppendageB->SetRelativeLocation(FVector(-30.0f, 155.0f, 260.0f));
        AppendageB->SetRelativeRotation(FRotator(0.0f, 180.0f, 0.0f));
        AppendageC->SetRelativeLocation(FVector(25.0f, -48.0f, 500.0f));
        AppendageD->SetRelativeLocation(FVector(25.0f, 48.0f, 500.0f));
        AppendageC->SetRelativeRotation(FRotator(-28.0f, -18.0f, 0.0f));
        AppendageD->SetRelativeRotation(FRotator(-28.0f, 18.0f, 0.0f));

        if (!bProductionFoundation)
        {
            Core->SetRelativeScale3D(FVector(1.15f, 0.90f, 2.40f));
            Head->SetRelativeScale3D(FVector(0.78f));
            AppendageA->SetRelativeScale3D(FVector(2.6f, 0.14f, 1.9f));
            AppendageB->SetRelativeScale3D(FVector(2.6f, 0.14f, 1.9f));
            AppendageC->SetRelativeScale3D(FVector(0.13f, 0.13f, 1.20f));
            AppendageD->SetRelativeScale3D(FVector(0.13f, 0.13f, 1.20f));
        }

        ThreatLight->SetRelativeLocation(FVector(80.0f, 0.0f, 280.0f));
        ThreatLight->SetIntensity(7800.0f);
        ThreatLight->SetVisibility(bThreatActive);
    }

    UMaterialInterface* BasicMaterial = LoadObject<UMaterialInterface>(
        nullptr, TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));
    if (BasicMaterial && !bProductionFoundation)
    {
        const FLinearColor BaseColor =
            ThreatType == EFellowshipMythicThreatType::Watcher
                ? FLinearColor(0.065f, 0.11f, 0.105f)
                : FLinearColor(0.055f, 0.022f, 0.015f);
        for (UStaticMeshComponent* Piece : Pieces)
        {
            if (!Piece || !Piece->IsVisible())
            {
                continue;
            }
            if (UMaterialInstanceDynamic* MID = UMaterialInstanceDynamic::Create(BasicMaterial, this))
            {
                MID->SetVectorParameterValue(TEXT("Color"), BaseColor);
                Piece->SetMaterial(0, MID);
            }
        }
    }

    UE_LOG(
        LogTemp,
        Display,
        TEXT("MythicThreatVisual: type=%s productionFoundation=%s gameplayCollision=off killable=no"),
        ThreatType == EFellowshipMythicThreatType::Watcher ? TEXT("Watcher") : TEXT("Balrog"),
        bProductionFoundation ? TEXT("yes") : TEXT("fallback"));
}

void AFellowshipMythicThreat::UpdateWatcherMotion(float DeltaSeconds)
{
    MotionTime += DeltaSeconds;
    UStaticMeshComponent* Tentacles[] = { AppendageA, AppendageB, AppendageC, AppendageD };
    for (int32 Index = 0; Index < 4; ++Index)
    {
        const float Phase = MotionTime * (1.35f + Index * 0.13f) + Index * 0.85f;
        const float Pitch = -68.0f + FMath::Sin(Phase) * (12.0f + Index * 2.0f);
        const float Yaw = Index * 75.0f - 50.0f + FMath::Cos(Phase * 0.74f) * 18.0f;
        Tentacles[Index]->SetRelativeRotation(FRotator(Pitch, Yaw, FMath::Sin(Phase * 1.2f) * 8.0f));
    }
    Core->SetRelativeLocation(FVector(0.0f, 0.0f, -35.0f + FMath::Sin(MotionTime * 1.1f) * 7.0f));
}

void AFellowshipMythicThreat::UpdateBalrogMotion(float DeltaSeconds)
{
    MotionTime += DeltaSeconds;
    const float WingPulse = FMath::Sin(MotionTime * 1.4f) * 6.0f;
    AppendageA->SetRelativeRotation(FRotator(-6.0f + WingPulse, -12.0f, -4.0f));
    AppendageB->SetRelativeRotation(FRotator(-6.0f + WingPulse, 192.0f, 4.0f));
    Core->SetRelativeLocation(FVector(0.0f, 0.0f, 170.0f + FMath::Sin(MotionTime * 2.0f) * 4.0f));
    ThreatLight->SetIntensity(7200.0f + (FMath::Sin(MotionTime * 7.0f) + 1.0f) * 1500.0f);
}

void AFellowshipMythicThreat::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    UpdateActivation();

    if (!bThreatActive)
    {
        return;
    }

    // Low-spec safeguard: retain visible motion close to the player, but reduce
    // update frequency when the mythic silhouette is only distant scenery.
    if (APawn* PlayerPawn = UGameplayStatics::GetPlayerPawn(this, 0))
    {
        const float Distance = FVector::Dist2D(GetActorLocation(), PlayerPawn->GetActorLocation());
        PrimaryActorTick.TickInterval = Distance > 5200.0f ? 0.22f : (Distance > 2800.0f ? 0.12f : 0.06f);
    }

    if (ThreatType == EFellowshipMythicThreatType::Watcher)
    {
        UpdateWatcherMotion(DeltaSeconds);
    }
    else
    {
        UpdateBalrogMotion(DeltaSeconds);
    }
}
