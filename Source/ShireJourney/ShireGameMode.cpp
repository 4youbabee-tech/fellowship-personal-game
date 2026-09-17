#include "ShireGameMode.h"
#include "ShireHUD.h"
#include "ShirePlayerCharacter.h"
#include "ShirePrototypeWorldBuilder.h"
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

    // This lets the starter run on an Engine template map before a final .umap exists.
    GetWorld()->SpawnActor<AShirePrototypeWorldBuilder>(FVector::ZeroVector, FRotator::ZeroRotator);

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
