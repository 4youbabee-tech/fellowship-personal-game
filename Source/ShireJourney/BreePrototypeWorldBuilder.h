#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "BreePrototypeWorldBuilder.generated.h"

class UStaticMesh;
class UMaterialInterface;
class AStaticMeshActor;

UCLASS()
class SHIREJOURNEY_API ABreePrototypeWorldBuilder : public AActor
{
    GENERATED_BODY()

public:
    ABreePrototypeWorldBuilder();
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
    void SpawnBreeTown();
    void SpawnStoryFlow();
};
