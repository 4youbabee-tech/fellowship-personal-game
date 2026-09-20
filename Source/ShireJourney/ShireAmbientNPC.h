#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ShireAmbientNPC.generated.h"

class USceneComponent;
class UStaticMeshComponent;
class UTextRenderComponent;

UCLASS()
class SHIREJOURNEY_API AShireAmbientNPC : public AActor
{
    GENERATED_BODY()

public:
    AShireAmbientNPC();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Routine")
    FVector RoutinePointA = FVector::ZeroVector;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Routine")
    FVector RoutinePointB = FVector(350.0f, 0.0f, 0.0f);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Routine")
    float WalkSpeed = 55.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Routine")
    float MinWait = 1.5f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Routine")
    float MaxWait = 5.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Routine")
    FName RoutineRole = TEXT("Villager");

    // Optional cheap visual activity carried by this ambient actor.
    // Examples: Basket, Crate, Satchel, Mug, Book, Lantern.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Routine")
    FName ActivityPropType = NAME_None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Awareness")
    bool bCanNoticePlayer = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Awareness")
    float PlayerNoticeRadius = 280.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Awareness")
    float MinObserveDuration = 1.2f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Awareness")
    float MaxObserveDuration = 2.8f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Awareness")
    float NoticeCooldown = 7.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Awareness", meta=(ClampMin="1.0", ClampMax="2.0"))
    float RunningNoticeMultiplier = 1.35f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Performance")
    float ReducedTickDistance = 3500.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Performance")
    float DormantTickDistance = 9000.0f;

private:
    UPROPERTY()
    USceneComponent* Root;

    UPROPERTY()
    UStaticMeshComponent* Torso;

    UPROPERTY()
    UStaticMeshComponent* Head;

    UPROPERTY()
    UStaticMeshComponent* Hair;

    UPROPERTY()
    UStaticMeshComponent* LeftArm;

    UPROPERTY()
    UStaticMeshComponent* RightArm;

    UPROPERTY()
    UStaticMeshComponent* LeftLeg;

    UPROPERTY()
    UStaticMeshComponent* RightLeg;

    UPROPERTY()
    UStaticMeshComponent* ActivityProp;

    UPROPERTY()
    UTextRenderComponent* SocialCaption;

    bool bHeadingToB = true;
    bool bObservingPlayer = false;
    float WaitRemaining = 0.0f;
    float WalkPhase = 0.0f;
    float ActivityPhase = 0.0f;
    float AnimationRateScale = 1.0f;
    float IdleLookAmplitude = 4.0f;
    float IdleLookPhase = 0.0f;
    FVector ActivityPropBase = FVector::ZeroVector;
    FRotator ActivityPropBaseRotation = FRotator::ZeroRotator;
    float SenseAccumulator = 0.0f;
    float ObserveRemaining = 0.0f;
    float NoticeCooldownRemaining = 0.0f;
    float SocialCheckRemaining = 0.0f;
    float SocialRemaining = 0.0f;
    float SocialCaptionDelay = 0.0f;
    float SocialCaptionRemaining = 0.0f;
    float LastPartnerCooldownRemaining = 0.0f;
    float ScheduleCheckRemaining = 0.0f;
    float NeedsCheckRemaining = 0.0f;
    float BaseWalkSpeed = 55.0f;
    float Hunger01 = 0.0f;
    float Fatigue01 = 0.0f;
    float SocialNeed01 = 0.0f;
    float Fear01 = 0.0f;
    FName RuntimeSchedulePhase = NAME_None;
    FName RuntimeEmotion = TEXT("CALM");
    FName RuntimeGoal = TEXT("ROUTINE");
    bool bSocializing = false;
    FText PendingSocialCaption;
    float VisualTorsoBaseZ = 58.0f;
    float VisualHeadBaseZ = 101.0f;
    float VisualHairBaseZ = 109.0f;
    FName AppliedVisualRole = NAME_None;
    TWeakObjectPtr<APawn> ObservedPlayer;
    TWeakObjectPtr<AShireAmbientNPC> SocialPartner;
    TWeakObjectPtr<AShireAmbientNPC> LastSocialPartner;
    FRandomStream Random;

    void ApplyVisualStyle();
    void UpdateWalkAnimation(float DeltaSeconds, bool bMoving);
    void UpdateAwareness(float DeltaSeconds);
    void UpdateSocialLife(float DeltaSeconds);
    void UpdateSocialCaption(float DeltaSeconds);
    void BeginSocialCaption(const FText& Text, float Delay, float Duration);
    FText ResolveAmbientConversationLine(bool bResponse) const;
    FName ResolveRuntimeProfileHint() const;
    void UpdateScheduleContext(float DeltaSeconds);
    void UpdateNeedsAndEmotion(float DeltaSeconds);
};
