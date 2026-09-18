#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ShirePrototypeWorldBuilder.generated.h"

class UStaticMesh;
class UMaterialInterface;
class AStaticMeshActor;

UCLASS()
class SHIREJOURNEY_API AShirePrototypeWorldBuilder : public AActor
{
    GENERATED_BODY()

public:
    AShirePrototypeWorldBuilder();
    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category="Prototype")
    void BuildPrototypeWorld();

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
    void SpawnHobbitHole(const FVector& Location, float Scale = 1.0f);
    void SpawnFenceLine(const FVector& Start, const FVector& End, int32 Sections);
    void SpawnGardenPatch(const FVector& Center, float Scale = 1.0f);
    void SpawnVillage();
    void SpawnSideStories();
    void SpawnStoryActors();
};
