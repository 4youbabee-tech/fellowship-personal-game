#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ShirePrototypeWorldBuilder.generated.h"

class UStaticMesh;
class UMaterialInterface;
class USceneComponent;
class UHierarchicalInstancedStaticMeshComponent;
class AStaticMeshActor;
class ADirectionalLight;
class ASkyLight;
class APostProcessVolume;
class UShireQuestSubsystem;

UCLASS()
class SHIREJOURNEY_API AShirePrototypeWorldBuilder : public AActor
{
    GENERATED_BODY()

public:
    AShirePrototypeWorldBuilder();
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UFUNCTION(BlueprintCallable, Category="Prototype")
    void BuildPrototypeWorld();

private:
    UPROPERTY() UStaticMesh* CubeMesh;
    UPROPERTY() UStaticMesh* SphereMesh;
    UPROPERTY() UStaticMesh* CylinderMesh;
    UPROPERTY() UStaticMesh* ConeMesh;
    UPROPERTY() UStaticMesh* ProductionTreeTrunkMesh = nullptr;
    UPROPERTY() UStaticMesh* ProductionTreeCanopyMesh = nullptr;
    UPROPERTY() UStaticMesh* ProductionRockMesh = nullptr;
    UPROPERTY() UStaticMesh* ProductionCrateMesh = nullptr;
    UPROPERTY() UStaticMesh* ProductionSignpostMesh = nullptr;
    UPROPERTY() UStaticMesh* ProductionBarrelMesh = nullptr;
    UPROPERTY() UStaticMesh* ProductionGroundBlockMesh = nullptr;
    UPROPERTY() UStaticMesh* ProductionRoadBlockMesh = nullptr;
    UPROPERTY() UStaticMesh* ProductionTurfMoundMesh = nullptr;
    UPROPERTY() UStaticMesh* ProductionHedgeMesh = nullptr;
    UPROPERTY() UStaticMesh* ProductionShrubMesh = nullptr;
    UPROPERTY() UStaticMesh* ProductionPathStoneMesh = nullptr;
    UPROPERTY() UStaticMesh* ProductionGrassClumpMesh = nullptr;
    UPROPERTY() UStaticMesh* ProductionFenceSegmentMesh = nullptr;
    UPROPERTY() UStaticMesh* ProductionHobbitFacadeMesh = nullptr;
    UPROPERTY() UStaticMesh* ProductionCartMesh = nullptr;
    UPROPERTY() UStaticMesh* ProductionBenchMesh = nullptr;
    UPROPERTY() UStaticMesh* ProductionMillWheelMesh = nullptr;
    UPROPERTY() UStaticMesh* ProductionLanternMesh = nullptr;
    UPROPERTY() UMaterialInterface* BasicMaterial;

    UPROPERTY() USceneComponent* RuntimeRoot;
    UPROPERTY() UHierarchicalInstancedStaticMeshComponent* GrassInstances;
    UPROPERTY() UHierarchicalInstancedStaticMeshComponent* FlowerInstances;
    UPROPERTY() UHierarchicalInstancedStaticMeshComponent* ShrubInstances;
    UPROPERTY() UHierarchicalInstancedStaticMeshComponent* DistantTreeTrunkInstances;
    UPROPERTY() UHierarchicalInstancedStaticMeshComponent* DistantTreeCanopyInstances;
    UPROPERTY() UHierarchicalInstancedStaticMeshComponent* RockInstances;
    UPROPERTY() UHierarchicalInstancedStaticMeshComponent* PathStoneInstances;
    UPROPERTY() ADirectionalLight* RuntimeSun = nullptr;
    UPROPERTY() ASkyLight* RuntimeSky = nullptr;
    UPROPERTY() APostProcessVolume* RuntimePostProcess = nullptr;
    UPROPERTY() UShireQuestSubsystem* QuestSubsystem = nullptr;

    bool bBuilt = false;

    AStaticMeshActor* SpawnShape(UStaticMesh* Mesh, const FVector& Location, const FVector& Scale,
        const FLinearColor& Color, const FRotator& Rotation = FRotator::ZeroRotator, bool bCollision = true);
    void SpawnLabel(const FString& Text, const FVector& Location, const FLinearColor& Color = FLinearColor::White);
    void SpawnTree(const FVector& Location, float Scale = 1.0f);
    void SpawnHobbitHole(const FVector& Location, float Scale = 1.0f);
    void SpawnFenceLine(const FVector& Start, const FVector& End, int32 Sections);
    void SpawnGardenPatch(const FVector& Center, float Scale = 1.0f);
    void ConfigureMorningAtmosphere();
    void ConfigureFoliageInstances();
    void SpawnFoliagePass();
    void SpawnScenicDetailPass();
    void SpawnVillage();
    void SpawnSideStories();
    void SpawnStoryActors();
    void ApplyStoryAtmosphere();

    UFUNCTION()
    void HandleActiveQuestChanged(FName QuestId);

    UFUNCTION()
    void HandleQuestStageChanged(FName QuestId, int32 NewStage);

    UFUNCTION()
    void HandleStoryBeatTriggered(FName StoryBeatId);
};
