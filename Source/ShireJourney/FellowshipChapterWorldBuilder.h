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
    UPROPERTY() UStaticMesh* WeathertopArchMesh = nullptr;
    UPROPERTY() UStaticMesh* WeathertopPillarMesh = nullptr;
    UPROPERTY() UStaticMesh* WeathertopCampRingMesh = nullptr;
    UPROPERTY() UStaticMesh* RivendellPavilionMesh = nullptr;
    UPROPERTY() UStaticMesh* RivendellArchMesh = nullptr;
    UPROPERTY() UStaticMesh* RivendellBridgeMesh = nullptr;
    UPROPERTY() UStaticMesh* RivendellLanternMesh = nullptr;
    UPROPERTY() UStaticMesh* RoadCampTentMesh = nullptr;
    UPROPERTY() UStaticMesh* RoadSupplyRackMesh = nullptr;
    UPROPERTY() UStaticMesh* CaradhrasRockMesh = nullptr;
    UPROPERTY() UStaticMesh* MoriaPillarMesh = nullptr;
    UPROPERTY() UStaticMesh* MoriaDoorMesh = nullptr;
    UPROPERTY() UStaticMesh* MoriaBrazierMesh = nullptr;
    UPROPERTY() UStaticMesh* MoriaBridgeMesh = nullptr;
    UPROPERTY() UStaticMesh* MoriaWallPanelMesh = nullptr;
    UPROPERTY() UStaticMesh* MoriaFloorSlabMesh = nullptr;
    UPROPERTY() UStaticMesh* MoriaArchMesh = nullptr;
    UPROPERTY() UStaticMesh* MoriaCeilingRibMesh = nullptr;
    UPROPERTY() UStaticMesh* MoriaBridgePierMesh = nullptr;
    UPROPERTY() UStaticMesh* MoriaTombDaisMesh = nullptr;
    UPROPERTY() UStaticMesh* MoriaReliefPanelMesh = nullptr;
    UPROPERTY() UStaticMesh* MoriaMineRailMesh = nullptr;
    UPROPERTY() UStaticMesh* MoriaOreCrateMesh = nullptr;
    UPROPERTY() UStaticMesh* MoriaCollapsedBeamMesh = nullptr;
    UPROPERTY() UStaticMesh* MoriaTorchNicheMesh = nullptr;
    UPROPERTY() UStaticMesh* MoriaChasmButtressMesh = nullptr;
    UPROPERTY() UStaticMesh* MoriaSideDoorMesh = nullptr;
    UPROPERTY() UStaticMesh* MoriaDebrisClusterMesh = nullptr;
    UPROPERTY() UStaticMesh* LorienTalanMesh = nullptr;
    UPROPERTY() UStaticMesh* LorienLanternMesh = nullptr;
    UPROPERTY() UStaticMesh* LorienMirrorMesh = nullptr;
    UPROPERTY() UStaticMesh* AnduinBoatMesh = nullptr;
    UPROPERTY() UStaticMesh* AmonHenStairMesh = nullptr;
    UPROPERTY() UStaticMesh* AmonHenRuinMesh = nullptr;
    UPROPERTY() UStaticMesh* ArgonathSentinelMesh = nullptr;
    UPROPERTY() UStaticMesh* CommonMountainRidgeMesh = nullptr;
    UPROPERTY() UStaticMesh* CommonCliffWallMesh = nullptr;
    UPROPERTY() UStaticMesh* CommonTerracedHillMesh = nullptr;
    UPROPERTY() UStaticMesh* CommonRiverBankMesh = nullptr;
    UPROPERTY() UStaticMesh* CommonBoulderClusterMesh = nullptr;
    UPROPERTY() UStaticMesh* CommonPineTreeMesh = nullptr;
    UPROPERTY() UStaticMesh* CommonBroadleafTreeMesh = nullptr;
    UPROPERTY() UStaticMesh* CommonGoldenTreeMesh = nullptr;
    UPROPERTY() UStaticMesh* CommonFallenLogMesh = nullptr;
    UPROPERTY() UStaticMesh* CommonDryStoneWallMesh = nullptr;
    UPROPERTY() UStaticMesh* CommonPathMarkerMesh = nullptr;
    UPROPERTY() UStaticMesh* CommonVillageFenceMesh = nullptr;
    UPROPERTY() UStaticMesh* CommonWoodPileMesh = nullptr;
    UPROPERTY() UStaticMesh* CommonFernClumpMesh = nullptr;
    UPROPERTY() UStaticMesh* CommonReedClusterMesh = nullptr;
    UPROPERTY() UStaticMesh* CommonRuinSlabMesh = nullptr;
    UPROPERTY() UStaticMesh* CommonFootbridgeMesh = nullptr;

    bool bBuilt = false;
    bool bProductionMeshesLoaded = false;

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
    void SpawnDiscoveryTrigger(
        const FVector& Location,
        FName DiscoveryId,
        const FString& DisplayName,
        FName OpensAfterStoryBeat,
        FName ClosesBeforeStoryBeat);

    void EnsureProductionMeshes();
    void ConfigureChapterAtmosphere(FName ChapterId);
    void SpawnProductionChapterLayer(FName ChapterId);
    void BuildWeathertop();
    void BuildRivendell();
    void BuildFellowshipRoad();
    void BuildMoria();
    void BuildLothlorien();
    void BuildAnduinAmonHen();
};
