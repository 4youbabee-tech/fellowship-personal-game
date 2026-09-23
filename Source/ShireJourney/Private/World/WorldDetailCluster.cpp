#include "WorldDetailCluster.h"

#include "Components/HierarchicalInstancedStaticMeshComponent.h"
#include "Components/SceneComponent.h"

AWorldDetailCluster::AWorldDetailCluster()
{
    PrimaryActorTick.bCanEverTick = false;

    Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    SetRootComponent(Root);

    Instances = CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(TEXT("Instances"));
    Instances->SetupAttachment(Root);
    Instances->SetMobility(EComponentMobility::Movable);
    Instances->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Instances->SetGenerateOverlapEvents(false);
    Instances->bCastDynamicShadow = false;
    Instances->bCastStaticShadow = false;
}

void AWorldDetailCluster::Configure(
    UStaticMesh* InMesh,
    bool bCollision,
    int32 StartCullDistance,
    int32 EndCullDistance)
{
    if (!Instances)
    {
        return;
    }

    Instances->SetStaticMesh(InMesh);
    Instances->SetCollisionEnabled(
        bCollision ? ECollisionEnabled::QueryAndPhysics : ECollisionEnabled::NoCollision);
    Instances->SetCullDistances(
        FMath::Max(0, StartCullDistance),
        FMath::Max(StartCullDistance + 100, EndCullDistance));
}

void AWorldDetailCluster::AddDetailInstance(
    const FVector& WorldLocation,
    const FRotator& WorldRotation,
    const FVector& Scale)
{
    if (!Instances || !Instances->GetStaticMesh())
    {
        return;
    }

    const FTransform WorldTransform(WorldRotation, WorldLocation, Scale);
    Instances->AddInstanceWorldSpace(WorldTransform);
}

int32 AWorldDetailCluster::GetDetailCount() const
{
    return Instances ? Instances->GetInstanceCount() : 0;
}
