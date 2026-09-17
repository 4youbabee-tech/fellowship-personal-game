#include "ShirePlayerCharacter.h"
#include "ShireInteractable.h"
#include "ShireQuestSubsystem.h"
#include "ShireSaveGame.h"
#include "ShireHUD.h"
#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/InputComponent.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/Controller.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/SpringArmComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/GameInstance.h"
#include "UObject/ConstructorHelpers.h"

namespace ShireSaveConstants
{
    static const FString SlotName(TEXT("ShireJourney_Auto"));
    static const int32 UserIndex = 0;
}

namespace ShireDebugChapters
{
    static const FName ChapterIds[] = {
        TEXT("P1C01"), TEXT("P1C02"), TEXT("P1C03"), TEXT("P1C04"),
        TEXT("P1C05"), TEXT("P1C06"), TEXT("P1C07"), TEXT("P1C08")
    };

    static const FName StartQuests[] = {
        TEXT("ShireArrival"), TEXT("RoadToBree"), TEXT("RoadToWeathertop"), TEXT("RivendellRecovery"),
        TEXT("SouthwardJourney"), TEXT("MoriaDark"), TEXT("LothlorienRest"), TEXT("AnduinJourney")
    };

    static const int32 Count = UE_ARRAY_COUNT(ChapterIds);
}

AShirePlayerCharacter::AShirePlayerCharacter()
{
    PrimaryActorTick.bCanEverTick = false;
    GetCapsuleComponent()->SetCapsuleRadius(28.0f);
    GetCapsuleComponent()->SetCapsuleHalfHeight(60.0f);

    bUseControllerRotationPitch = false;
    bUseControllerRotationYaw = false;
    bUseControllerRotationRoll = false;

    GetCharacterMovement()->bOrientRotationToMovement = true;
    GetCharacterMovement()->RotationRate = FRotator(0.0f, 480.0f, 0.0f);
    GetCharacterMovement()->MaxWalkSpeed = WalkSpeed;
    GetCharacterMovement()->GetNavAgentPropertiesRef().bCanCrouch = true;

    CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
    CameraBoom->SetupAttachment(RootComponent);
    CameraBoom->TargetArmLength = 315.0f;
    CameraBoom->bUsePawnControlRotation = true;
    CameraBoom->bEnableCameraLag = true;
    CameraBoom->CameraLagSpeed = 11.0f;
    CameraBoom->SetRelativeLocation(FVector(0.0f, 0.0f, 58.0f));

    FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
    FollowCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
    FollowCamera->bUsePawnControlRotation = false;

    PrototypeTorso = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypeTorso"));
    PrototypeTorso->SetupAttachment(GetCapsuleComponent());
    PrototypeTorso->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    PrototypeTorso->SetRelativeLocation(FVector(0.0f, 0.0f, -14.0f));
    PrototypeTorso->SetRelativeScale3D(FVector(0.34f, 0.34f, 0.58f));

    PrototypeHead = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypeHead"));
    PrototypeHead->SetupAttachment(GetCapsuleComponent());
    PrototypeHead->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    PrototypeHead->SetRelativeLocation(FVector(0.0f, 0.0f, 38.0f));
    PrototypeHead->SetRelativeScale3D(FVector(0.25f));

    static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderMesh(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> SphereMesh(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
    if (CylinderMesh.Succeeded()) PrototypeTorso->SetStaticMesh(CylinderMesh.Object);
    if (SphereMesh.Succeeded()) PrototypeHead->SetStaticMesh(SphereMesh.Object);
}

void AShirePlayerCharacter::BeginPlay()
{
    Super::BeginPlay();
    GetCharacterMovement()->MaxWalkSpeed = WalkSpeed;
}

void AShirePlayerCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);

    PlayerInputComponent->BindAxis(TEXT("MoveForward"), this, &AShirePlayerCharacter::MoveForward);
    PlayerInputComponent->BindAxis(TEXT("MoveRight"), this, &AShirePlayerCharacter::MoveRight);
    PlayerInputComponent->BindAxis(TEXT("Turn"), this, &AShirePlayerCharacter::TurnAtRate);
    PlayerInputComponent->BindAxis(TEXT("LookUp"), this, &AShirePlayerCharacter::LookUpAtRate);

    PlayerInputComponent->BindAction(TEXT("Jump"), IE_Pressed, this, &ACharacter::Jump);
    PlayerInputComponent->BindAction(TEXT("Jump"), IE_Released, this, &ACharacter::StopJumping);
    PlayerInputComponent->BindAction(TEXT("Crouch"), IE_Pressed, this, &AShirePlayerCharacter::StartCrouch);
    PlayerInputComponent->BindAction(TEXT("Crouch"), IE_Released, this, &AShirePlayerCharacter::StopCrouch);
    PlayerInputComponent->BindAction(TEXT("Sprint"), IE_Pressed, this, &AShirePlayerCharacter::StartSprint);
    PlayerInputComponent->BindAction(TEXT("Sprint"), IE_Released, this, &AShirePlayerCharacter::StopSprint);
    PlayerInputComponent->BindAction(TEXT("Interact"), IE_Pressed, this, &AShirePlayerCharacter::Interact);
    PlayerInputComponent->BindAction(TEXT("QuickSave"), IE_Pressed, this, &AShirePlayerCharacter::QuickSave);
    PlayerInputComponent->BindAction(TEXT("QuickLoad"), IE_Pressed, this, &AShirePlayerCharacter::QuickLoad);
    PlayerInputComponent->BindAction(TEXT("DebugPreviousChapter"), IE_Pressed, this, &AShirePlayerCharacter::DebugPreviousChapter);
    PlayerInputComponent->BindAction(TEXT("DebugNextChapter"), IE_Pressed, this, &AShirePlayerCharacter::DebugNextChapter);
}

void AShirePlayerCharacter::MoveForward(float Value)
{
    if (Controller && !FMath::IsNearlyZero(Value))
    {
        const FRotator Rotation = Controller->GetControlRotation();
        const FRotator YawRotation(0.0f, Rotation.Yaw, 0.0f);
        AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X), Value);
    }
}

void AShirePlayerCharacter::MoveRight(float Value)
{
    if (Controller && !FMath::IsNearlyZero(Value))
    {
        const FRotator Rotation = Controller->GetControlRotation();
        const FRotator YawRotation(0.0f, Rotation.Yaw, 0.0f);
        AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y), Value);
    }
}

void AShirePlayerCharacter::TurnAtRate(float Value)
{
    AddControllerYawInput(Value * BaseTurnRate * GetWorld()->GetDeltaSeconds());
}

void AShirePlayerCharacter::LookUpAtRate(float Value)
{
    AddControllerPitchInput(Value * BaseLookUpRate * GetWorld()->GetDeltaSeconds());
}

void AShirePlayerCharacter::StartSprint()
{
    GetCharacterMovement()->MaxWalkSpeed = SprintSpeed;
}

void AShirePlayerCharacter::StopSprint()
{
    GetCharacterMovement()->MaxWalkSpeed = WalkSpeed;
}

void AShirePlayerCharacter::StartCrouch()
{
    Crouch();
}

void AShirePlayerCharacter::StopCrouch()
{
    UnCrouch();
}

void AShirePlayerCharacter::Interact()
{
    if (!FollowCamera || !GetWorld())
    {
        return;
    }

    const FVector Start = FollowCamera->GetComponentLocation();
    const FVector End = Start + FollowCamera->GetForwardVector() * InteractionDistance;

    FHitResult Hit;
    FCollisionQueryParams Params(SCENE_QUERY_STAT(ShireInteract), false, this);
    if (GetWorld()->LineTraceSingleByChannel(Hit, Start, End, ECC_Visibility, Params))
    {
        AActor* HitActor = Hit.GetActor();
        if (HitActor && HitActor->GetClass()->ImplementsInterface(UShireInteractable::StaticClass()))
        {
            IShireInteractable::Execute_Interact(HitActor, this);
            return;
        }
    }

    if (APlayerController* PC = Cast<APlayerController>(Controller))
    {
        if (AShireHUD* HUD = Cast<AShireHUD>(PC->GetHUD()))
        {
            HUD->ShowAlert(FText::FromString(TEXT("Nothing nearby to interact with.")), 1.5f);
        }
    }
}

void AShirePlayerCharacter::QuickSave()
{
    UShireSaveGame* Save = Cast<UShireSaveGame>(UGameplayStatics::CreateSaveGameObject(UShireSaveGame::StaticClass()));
    if (!Save)
    {
        return;
    }

    Save->PlayerLocation = GetActorLocation();
    Save->PlayerRotation = GetActorRotation();

    if (UGameInstance* GI = GetGameInstance())
    {
        if (UShireQuestSubsystem* QuestSubsystem = GI->GetSubsystem<UShireQuestSubsystem>())
        {
            Save->QuestStages = QuestSubsystem->GetAllQuestStages();
            Save->ActiveQuestId = QuestSubsystem->GetActiveQuestId();
            Save->CurrentChapterId = QuestSubsystem->GetCurrentChapterId();
            Save->CompletedStoryBeats = QuestSubsystem->GetCompletedStoryBeats();
        }
    }

    const bool bSaved = UGameplayStatics::SaveGameToSlot(Save, ShireSaveConstants::SlotName, ShireSaveConstants::UserIndex);
    if (APlayerController* PC = Cast<APlayerController>(Controller))
    {
        if (AShireHUD* HUD = Cast<AShireHUD>(PC->GetHUD()))
        {
            HUD->ShowAlert(FText::FromString(bSaved ? TEXT("Journey saved.") : TEXT("Save failed.")), 1.8f);
        }
    }
}

void AShirePlayerCharacter::QuickLoad()
{
    if (!UGameplayStatics::DoesSaveGameExist(ShireSaveConstants::SlotName, ShireSaveConstants::UserIndex))
    {
        if (APlayerController* PC = Cast<APlayerController>(Controller))
        {
            if (AShireHUD* HUD = Cast<AShireHUD>(PC->GetHUD()))
            {
                HUD->ShowAlert(FText::FromString(TEXT("No save found yet.")), 1.8f);
            }
        }
        return;
    }

    UShireSaveGame* Save = Cast<UShireSaveGame>(UGameplayStatics::LoadGameFromSlot(
        ShireSaveConstants::SlotName, ShireSaveConstants::UserIndex));
    if (!Save)
    {
        return;
    }

    if (UGameInstance* GI = GetGameInstance())
    {
        if (UShireQuestSubsystem* QuestSubsystem = GI->GetSubsystem<UShireQuestSubsystem>())
        {
            QuestSubsystem->RestoreQuestState(
                Save->QuestStages,
                Save->ActiveQuestId,
                Save->CurrentChapterId,
                Save->CompletedStoryBeats);
        }
    }

    SetActorLocationAndRotation(Save->PlayerLocation, Save->PlayerRotation, false, nullptr, ETeleportType::TeleportPhysics);

    if (APlayerController* PC = Cast<APlayerController>(Controller))
    {
        if (AShireHUD* HUD = Cast<AShireHUD>(PC->GetHUD()))
        {
            HUD->ShowAlert(FText::FromString(TEXT("Journey restored.")), 1.8f);
        }
    }
}

void AShirePlayerCharacter::DebugStartChapterByIndex(int32 ChapterIndex)
{
    if (ChapterIndex < 0 || ChapterIndex >= ShireDebugChapters::Count)
    {
        return;
    }

    UGameInstance* GI = GetGameInstance();
    UShireQuestSubsystem* QuestSubsystem = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    if (!QuestSubsystem)
    {
        return;
    }

    QuestSubsystem->StartChapter(
        ShireDebugChapters::ChapterIds[ChapterIndex],
        ShireDebugChapters::StartQuests[ChapterIndex],
        0);

    if (APlayerController* PC = Cast<APlayerController>(Controller))
    {
        if (AShireHUD* HUD = Cast<AShireHUD>(PC->GetHUD()))
        {
            HUD->ShowAlert(FText::FromString(FString::Printf(TEXT("Developer jump: %s"), *ShireDebugChapters::ChapterIds[ChapterIndex].ToString())), 2.0f);
        }
    }
}

void AShirePlayerCharacter::DebugPreviousChapter()
{
    UGameInstance* GI = GetGameInstance();
    UShireQuestSubsystem* QuestSubsystem = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    if (!QuestSubsystem)
    {
        return;
    }

    const FName Current = QuestSubsystem->GetCurrentChapterId();
    int32 CurrentIndex = 0;
    for (int32 Index = 0; Index < ShireDebugChapters::Count; ++Index)
    {
        if (ShireDebugChapters::ChapterIds[Index] == Current)
        {
            CurrentIndex = Index;
            break;
        }
    }

    DebugStartChapterByIndex(FMath::Max(0, CurrentIndex - 1));
}

void AShirePlayerCharacter::DebugNextChapter()
{
    UGameInstance* GI = GetGameInstance();
    UShireQuestSubsystem* QuestSubsystem = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    if (!QuestSubsystem)
    {
        return;
    }

    const FName Current = QuestSubsystem->GetCurrentChapterId();
    int32 CurrentIndex = 0;
    for (int32 Index = 0; Index < ShireDebugChapters::Count; ++Index)
    {
        if (ShireDebugChapters::ChapterIds[Index] == Current)
        {
            CurrentIndex = Index;
            break;
        }
    }

    DebugStartChapterByIndex(FMath::Min(ShireDebugChapters::Count - 1, CurrentIndex + 1));
}
