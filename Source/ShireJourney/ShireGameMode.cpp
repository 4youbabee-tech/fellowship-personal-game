#include "ShireGameMode.h"
#include "ChapterWorldRouter.h"
#include "ShireHUD.h"
#include "ShirePlayerCharacter.h"
#include "Kismet/GameplayStatics.h"
#include "GameFramework/PlayerController.h"

AShireGameMode::AShireGameMode()
{
    DefaultPawnClass = AShirePlayerCharacter::StaticClass();
    HUDClass = AShireHUD::StaticClass();
}

void AShireGameMode::BeginPlay()
{
    Super::BeginPlay();

    // Prototype chapter worlds are spawned through a router so Chapter 1 can hand off
    // to Bree without loading both regions at the same time.
    GetWorld()->SpawnActor<AChapterWorldRouter>(FVector::ZeroVector, FRotator::ZeroRotator);

    APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0);
    if (PC)
    {
        if (!PC->GetPawn())
        {
            RestartPlayerAtTransform(PC, FTransform(FRotator(0.0f, 0.0f, 0.0f), FVector(-2410.0f, -120.0f, 130.0f)));
        }
        else
        {
            PC->GetPawn()->SetActorLocationAndRotation(FVector(-2410.0f, -120.0f, 130.0f), FRotator(0.0f, 0.0f, 0.0f));
        }
    }
}
