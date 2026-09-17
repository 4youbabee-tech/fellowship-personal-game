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

    const FVector ToPlayer = PlayerPawn->GetActorLocation() - GetActorLocation();
    const float Distance = ToPlayer.Size2D();
    if (Distance > FollowDistance)
    {
        const FVector Step = ToPlayer.GetSafeNormal2D() * FollowSpeed * DeltaSeconds;
        AddActorWorldOffset(Step, true);
        SetActorRotation(ToPlayer.Rotation());
    }
}

void AShireNPC::Interact_Implementation(AActor* Interactor)
{
    UGameInstance* GI = GetGameInstance();
    UShireQuestSubsystem* QuestSubsystem = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;

    if (QuestSubsystem && QuestId != NAME_None && QuestSubsystem->GetQuestStage(QuestId) < RequiredQuestStage)
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
        if (QuestSubsystem->GetQuestStage(NextQuestId) < NextQuestStage)
        {
            QuestSubsystem->SetQuestStage(NextQuestId, NextQuestStage);
        }
    }

    if (bFollowPlayerAfterInteraction)
    {
        bFollowingPlayer = true;
    }
}
