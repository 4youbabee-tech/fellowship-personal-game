#include "ShireNPC.h"
#include "ShireQuestSubsystem.h"
#include "ShireHUD.h"
#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/GameInstance.h"
#include "GameFramework/PlayerController.h"
#include "UObject/ConstructorHelpers.h"

AShireNPC::AShireNPC()
{
    PrimaryActorTick.bCanEverTick = true;
    GetCapsuleComponent()->SetCapsuleRadius(28.0f);
    GetCapsuleComponent()->SetCapsuleHalfHeight(60.0f);
    DisplayName = FText::FromString(TEXT("Hobbit"));

    PrototypeTorso = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypeTorso"));
    PrototypeTorso->SetupAttachment(GetCapsuleComponent());
    PrototypeTorso->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    PrototypeTorso->SetRelativeLocation(FVector(0.0f, 0.0f, -15.0f));
    PrototypeTorso->SetRelativeScale3D(FVector(0.32f, 0.32f, 0.55f));

    PrototypeHead = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypeHead"));
    PrototypeHead->SetupAttachment(GetCapsuleComponent());
    PrototypeHead->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    PrototypeHead->SetRelativeLocation(FVector(0.0f, 0.0f, 36.0f));
    PrototypeHead->SetRelativeScale3D(FVector(0.24f));

    static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderMesh(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> SphereMesh(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
    if (CylinderMesh.Succeeded()) PrototypeTorso->SetStaticMesh(CylinderMesh.Object);
    if (SphereMesh.Succeeded()) PrototypeHead->SetStaticMesh(SphereMesh.Object);
}

int32 AShireNPC::ResolveCompanionSlot() const
{
    if (CompanionSlotIndex >= 0)
    {
        return CompanionSlotIndex;
    }

    const FString Name = DisplayName.ToString();
    if (Name.Equals(TEXT("Sam"), ESearchCase::IgnoreCase)) return 0;
    if (Name.Equals(TEXT("Merry"), ESearchCase::IgnoreCase)) return 1;
    if (Name.Equals(TEXT("Pippin"), ESearchCase::IgnoreCase)) return 2;
    if (Name.Equals(TEXT("Aragorn"), ESearchCase::IgnoreCase) || Name.Equals(TEXT("Strider"), ESearchCase::IgnoreCase)) return 3;
    if (Name.Equals(TEXT("Boromir"), ESearchCase::IgnoreCase)) return 4;
    if (Name.Equals(TEXT("Legolas"), ESearchCase::IgnoreCase)) return 5;
    if (Name.Equals(TEXT("Gimli"), ESearchCase::IgnoreCase)) return 6;
    if (Name.Equals(TEXT("Gandalf"), ESearchCase::IgnoreCase)) return 7;
    return 8;
}

FVector AShireNPC::GetFormationTarget(const APawn* PlayerPawn) const
{
    if (!PlayerPawn)
    {
        return GetActorLocation();
    }

    const int32 Slot = ResolveCompanionSlot();
    const int32 Row = Slot / 2;
    const float Side = (Slot % 2 == 0) ? -1.0f : 1.0f;
    const float BackDistance = FollowDistance + Row * (FormationSpacing * 0.85f);
    const float SideDistance = FormationSpacing * (1.0f + 0.15f * Row) * Side;

    const FVector Forward = PlayerPawn->GetActorForwardVector().GetSafeNormal2D();
    const FVector Right = PlayerPawn->GetActorRightVector().GetSafeNormal2D();
    FVector Target = PlayerPawn->GetActorLocation() - Forward * BackDistance + Right * SideDistance;
    Target.Z = PlayerPawn->GetActorLocation().Z;
    return Target;
}

void AShireNPC::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    if (!bFollowingPlayer || !GetWorld())
    {
        return;
    }

    APlayerController* PC = GetWorld()->GetFirstPlayerController();
    APawn* PlayerPawn = PC ? PC->GetPawn() : nullptr;
    if (!PlayerPawn)
    {
        return;
    }

    const FVector Target = GetFormationTarget(PlayerPawn);
    FVector ToTarget = Target - GetActorLocation();
    ToTarget.Z = 0.0f;
    const float Distance = ToTarget.Size();

    if (Distance > TeleportCatchUpDistance)
    {
        FVector SafeTarget = Target;
        SafeTarget.Z = PlayerPawn->GetActorLocation().Z;
        SetActorLocation(SafeTarget, false, nullptr, ETeleportType::TeleportPhysics);
        return;
    }

    if (Distance <= FollowAcceptanceRadius)
    {
        return;
    }

    const float EffectiveSpeed = Distance > CatchUpDistance ? FollowSpeed * 2.0f : FollowSpeed;
    const float MaxStep = EffectiveSpeed * DeltaSeconds;
    const FVector Step = ToTarget.GetSafeNormal() * FMath::Min(MaxStep, Distance - FollowAcceptanceRadius);
    AddActorWorldOffset(Step, true);

    if (!Step.IsNearlyZero())
    {
        const FRotator DesiredRotation = Step.Rotation();
        SetActorRotation(FMath::RInterpTo(GetActorRotation(), DesiredRotation, DeltaSeconds, 7.0f));
    }
}

void AShireNPC::Interact_Implementation(AActor* Interactor)
{
    UGameInstance* GI = GetGameInstance();
    UShireQuestSubsystem* QuestSubsystem = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;

    if (QuestSubsystem && QuestId != NAME_None)
    {
        if (QuestSubsystem->GetActiveQuestId() != QuestId || QuestSubsystem->GetQuestStage(QuestId) < RequiredQuestStage)
        {
            if (APlayerController* PC = GetWorld() ? GetWorld()->GetFirstPlayerController() : nullptr)
            {
                if (AShireHUD* HUD = Cast<AShireHUD>(PC->GetHUD()))
                {
                    HUD->ShowDialogue(DisplayName, FText::FromString(TEXT("Not now. There is something you must do first.")), 3.5f);
                }
            }
            return;
        }
    }

    if (DialogueLines.Num() > 0)
    {
        const FText& Line = DialogueLines[CurrentDialogueIndex % DialogueLines.Num()];
        if (APlayerController* PC = GetWorld() ? GetWorld()->GetFirstPlayerController() : nullptr)
        {
            if (AShireHUD* HUD = Cast<AShireHUD>(PC->GetHUD()))
            {
                HUD->ShowDialogue(DisplayName, Line, 6.0f);
            }
        }
        CurrentDialogueIndex = (CurrentDialogueIndex + 1) % DialogueLines.Num();
    }

    if (QuestSubsystem && QuestId != NAME_None && QuestStageAfterInteraction >= 0)
    {
        if (QuestSubsystem->GetQuestStage(QuestId) < QuestStageAfterInteraction)
        {
            QuestSubsystem->SetQuestStage(QuestId, QuestStageAfterInteraction);
        }
    }

    if (QuestSubsystem && NextQuestId != NAME_None)
    {
        QuestSubsystem->StartQuest(NextQuestId, NextQuestStage);
    }

    if (bFollowPlayerAfterInteraction)
    {
        bFollowingPlayer = true;
    }
}
