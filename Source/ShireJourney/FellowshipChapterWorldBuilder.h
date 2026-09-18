#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "FellowshipChapterWorldBuilder.generated.h"

class UStaticMesh;
class UMaterialInterface;
class AStaticMeshActor;
class AFellowshipEnemyPrototype;
class AShireNPC;
enum class EFellowshipEnemyType : uint8;

UCLASS()
class SHIREJOURNEY_API AFellowshipChapterWorldBuilder : public AActor
{
    GENERATED_BODY()

public:
    AFellowshipChapterWorldBuilder();

    UFUNCTION(BlueprintCallable, Category="Prototype")
    void BuildChapter(FName ChapterId);

private:
    UPROPERTY() UStaticMesh* CubeMesh;
    UPROPERTY() UStaticMesh* SphereMesh;
    UPROPERTY() UStaticMesh* CylinderMesh;
    UPROPERTY() UStaticMesh* ConeMesh;
    UPROPERTY() UMaterialInterface* BasicMaterial;

    bool bBuilt = false;

    AStaticMeshActor* SpawnShape(UStaticMesh* Mesh, const FVector& Location, const FVector& Scale,
        const FLinearColor& Color, const FRotator& Rotation = FRotator::ZeroRotator, bool bCollision = true);
    void SpawnLabel(const FString& Text, const FVector& Location, const FLinearColor& Color = FLinearColor::White);
    void SpawnTree(const FVector& Location, float Scale = 1.0f);
    AShireNPC* SpawnNPC(const FString& Name, const FVector& Location, const FRotator& Rotation,
        FName QuestId, int32 RequiredStage, int32 StageAfter, const FString& Line,
        FName NextQuestId = NAME_None, int32 NextQuestStage = 0, bool bFollow = false);
    AShireNPC* SpawnTravelCompanion(const FString& Name, const FVector& Location,
        const FString& Line, FName StopFollowingStoryBeat = NAME_None);
    AFellowshipEnemyPrototype* SpawnEnemy(EFellowshipEnemyType Type, const FVector& Location,
        const FRotator& Rotation, FName RequiredQuestId, int32 RequiredMinStage = 0);
    void SpawnQuestTrigger(const FVector& Location, FName QuestId, int32 RequiredStage, int32 StageAfter,
        const FString& Message, FName StoryBeatId = NAME_None, FName NextQuestId = NAME_None,
        int32 NextQuestStage = 0, FName NextChapterId = NAME_None, FName NextChapterQuestId = NAME_None,
        int32 NextChapterQuestStage = 0);

    void BuildWeathertop();
    void BuildRivendell();
    void BuildFellowshipRoad();
    void BuildMoria();
    void BuildLothlorien();
    void BuildAnduinAmonHen();
};
