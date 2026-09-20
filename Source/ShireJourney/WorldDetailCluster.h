#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "WorldDetailCluster.generated.h"

class UHierarchicalInstancedStaticMeshComponent;
class USceneComponent;
class UStaticMesh;

UCLASS()
class SHIREJOURNEY_API AWorldDetailCluster : public AActor
{
    GENERATED_BODY()

public:
    AWorldDetailCluster();

    void Configure(
        UStaticMesh* InMesh,
        bool bCollision,
        int32 StartCullDistance,
        int32 EndCullDistance);

    void AddDetailInstance(
        const FVector& WorldLocation,
        const FRotator& WorldRotation,
        const FVector& Scale);

    int32 GetDetailCount() const;

private:
    UPROPERTY()
    USceneComponent* Root = nullptr;

    UPROPERTY()
    UHierarchicalInstancedStaticMeshComponent* Instances = nullptr;
};
