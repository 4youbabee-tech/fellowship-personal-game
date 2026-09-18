#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "FellowshipEnemyPrototype.generated.h"

class UStaticMeshComponent;

UENUM(BlueprintType)
enum class EFellowshipEnemyType : uint8
{
    Orc,
    UrukHai,
    CaveTroll
};

UCLASS()
class SHIREJOURNEY_API AFellowshipEnemyPrototype : public ACharacter
{
    GENERATED_BODY()

public:
    AFellowshipEnemyPrototype();

    virtual void Tick(float DeltaSeconds) override;
    virtual float TakeDamage(float DamageAmount, struct FDamageEvent const& DamageEvent,
        class AController* EventInstigator, AActor* DamageCauser) override;

    UFUNCTION(BlueprintCallable, Category="Enemy")
    void ConfigureEnemy(EFellowshipEnemyType InType, FName InRequiredQuestId = NAME_None, int32 InRequiredMinStage = 0);

    UFUNCTION(BlueprintPure, Category="Enemy")
    bool IsDefeated() const { return bDefeated; }

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Enemy")
    EFellowshipEnemyType EnemyType = EFellowshipEnemyType::Orc;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Encounter")
    FName RequiredQuestId = NAME_None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Encounter")
    int32 RequiredMinStage = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combat")
    float MaxHealth = 55.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combat")
    float DetectionRadius = 900.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combat")
    float AttackRange = 135.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combat")
    float AttackDamage = 8.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combat")
    float AttackInterval = 1.25f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combat")
    float MoveSpeed = 185.0f;

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY() UStaticMeshComponent* Torso;
    UPROPERTY() UStaticMeshComponent* Head;
    UPROPERTY() UStaticMeshComponent* LeftArm;
    UPROPERTY() UStaticMeshComponent* RightArm;
    UPROPERTY() UStaticMeshComponent* LeftLeg;
    UPROPERTY() UStaticMeshComponent* RightLeg;
    UPROPERTY() UStaticMeshComponent* Weapon;

    FVector HomeLocation = FVector::ZeroVector;
    float CurrentHealth = 55.0f;
    float AttackCooldownRemaining = 0.0f;
    float WalkPhase = 0.0f;
    bool bProfileApplied = false;
    bool bDefeated = false;
    bool bEncounterActive = false;

    void ApplyTypeProfile();
    bool IsEncounterAllowed() const;
    void SetEncounterActive(bool bActive);
    void UpdateBehavior(float DeltaSeconds);
    void UpdateVisualMotion(float DeltaSeconds, bool bMoving);
    void AttackPlayer(class AShirePlayerCharacter* Player);
};
