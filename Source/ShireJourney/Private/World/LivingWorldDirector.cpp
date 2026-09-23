#include "LivingWorldDirector.h"
#include "ChapterWorldRouter.h"

#include "ShireAmbientNPC.h"
#include "ShireWorldEventInteraction.h"
#include "ShireNPCContextSubsystem.h"
#include "ShireQuestSubsystem.h"
#include "WorldAmbientMotionActor.h"

#include "Dom/JsonObject.h"
#include "Engine/GameInstance.h"
#include "Engine/StaticMesh.h"
#include "GameFramework/Pawn.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "UObject/SoftObjectPath.h"

ALivingWorldDirector::ALivingWorldDirector()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.TickInterval = 0.35f;
}

void ALivingWorldDirector::BeginPlay()
{
    Super::BeginPlay();

    Random.Initialize(7919);
    LoadEventContract();
    LoadLifeSaturationContract();

    if (UGameInstance* GI = GetGameInstance())
    {
        QuestSubsystem = GI->GetSubsystem<UShireQuestSubsystem>();
        if (QuestSubsystem)
        {
            QuestSubsystem->OnChapterChanged.AddDynamic(this, &ALivingWorldDirector::HandleChapterChanged);
            QuestSubsystem->OnExperienceChanged.AddDynamic(this, &ALivingWorldDirector::HandleExperienceChanged);
            ActiveChapterId = QuestSubsystem->GetCurrentChapterId();
        }
    }

    WorldRouter = Cast<AChapterWorldRouter>(UGameplayStatics::GetActorOfClass(
        this, AChapterWorldRouter::StaticClass()));
    if (AChapterWorldRouter* Router = WorldRouter.Get())
    {
        Router->OnWorldCommitted.AddUObject(
            this, &ALivingWorldDirector::HandleWorldCommitted);
    }

    SynchronizeCommittedWorld();
}

void ALivingWorldDirector::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (AChapterWorldRouter* Router = WorldRouter.Get())
    {
        Router->OnWorldCommitted.RemoveAll(this);
    }
    WorldRouter.Reset();

    if (QuestSubsystem)
    {
        QuestSubsystem->OnChapterChanged.RemoveDynamic(this, &ALivingWorldDirector::HandleChapterChanged);
        QuestSubsystem->OnExperienceChanged.RemoveDynamic(this, &ALivingWorldDirector::HandleExperienceChanged);
        QuestSubsystem = nullptr;
    }

    for (FActiveMicroEvent& Event : ActiveEvents)
    {
        for (TWeakObjectPtr<AActor>& ActorPtr : Event.Actors)
        {
            if (AActor* Actor = ActorPtr.Get())
            {
                Actor->Destroy();
            }
        }
    }
    ActiveEvents.Empty();

    for (TWeakObjectPtr<AShireAmbientNPC>& NPCPtr : BaselinePopulation)
    {
        if (AShireAmbientNPC* NPC = NPCPtr.Get())
        {
            NPC->Destroy();
        }
    }
    BaselinePopulation.Empty();

    for (TWeakObjectPtr<AShireAmbientNPC>& NPCPtr : AmbientNPCPool)
    {
        if (AShireAmbientNPC* NPC = NPCPtr.Get())
        {
            NPC->Destroy();
        }
    }
    AmbientNPCPool.Empty();

    Super::EndPlay(EndPlayReason);
}

bool ALivingWorldDirector::LoadEventContract()
{
    const FString Path = FPaths::Combine(FPaths::ProjectDir(), TEXT("Data/LivingWorldEventPlan.json"));
    FString JsonText;
    if (!FFileHelper::LoadFileToString(JsonText, *Path))
    {
        UE_LOG(LogTemp, Warning, TEXT("LivingWorldDirector: could not read %s; using safe defaults."), *Path);
        return false;
    }

    TSharedPtr<FJsonObject> Root;
    const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonText);
    if (!FJsonSerializer::Deserialize(Reader, Root) || !Root.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("LivingWorldDirector: invalid event contract; using safe defaults."));
        return false;
    }

    const TSharedPtr<FJsonObject>* Budgets = nullptr;
    if (Root->TryGetObjectField(TEXT("region_budgets"), Budgets) && Budgets && Budgets->IsValid())
    {
        double Value = 0.0;
        if ((*Budgets)->TryGetNumberField(TEXT("max_active_micro_events_near_player"), Value))
        {
            MaxActiveMicroEvents = FMath::Clamp(static_cast<int32>(Value), 1, 5);
        }
        if ((*Budgets)->TryGetNumberField(TEXT("min_seconds_between_event_starts"), Value))
        {
            MinSecondsBetweenEventStarts = FMath::Clamp(static_cast<float>(Value), 6.0f, 60.0f);
        }
        if ((*Budgets)->TryGetNumberField(TEXT("event_cull_distance_cm"), Value))
        {
            EventCullDistance = FMath::Clamp(static_cast<float>(Value), 2500.0f, 9000.0f);
        }
    }

    AllowedEventTypesByChapter.Empty();
    const TArray<TSharedPtr<FJsonValue>>* Contracts = nullptr;
    if (Root->TryGetArrayField(TEXT("chapter_contracts"), Contracts) && Contracts)
    {
        for (const TSharedPtr<FJsonValue>& ContractValue : *Contracts)
        {
            const TSharedPtr<FJsonObject> Contract =
                ContractValue.IsValid() ? ContractValue->AsObject() : nullptr;
            if (!Contract.IsValid())
            {
                continue;
            }

            FString ChapterString;
            Contract->TryGetStringField(TEXT("chapter"), ChapterString);
            if (ChapterString.IsEmpty())
            {
                continue;
            }

            TArray<FName> Allowed;
            const TArray<TSharedPtr<FJsonValue>>* AllowedValues = nullptr;
            if (Contract->TryGetArrayField(TEXT("allowed"), AllowedValues) && AllowedValues)
            {
                for (const TSharedPtr<FJsonValue>& AllowedValue : *AllowedValues)
                {
                    const FString TypeString = AllowedValue.IsValid() ? AllowedValue->AsString() : FString();
                    if (!TypeString.IsEmpty())
                    {
                        Allowed.Add(FName(*TypeString));
                    }
                }
            }
            AllowedEventTypesByChapter.Add(FName(*ChapterString), Allowed);
        }
    }

    return AllowedEventTypesByChapter.Num() > 0;
}

bool ALivingWorldDirector::LoadLifeSaturationContract()
{
    const FString Path = FPaths::Combine(FPaths::ProjectDir(), TEXT("Data/WorldLifeSaturationPlan.json"));
    FString JsonText;
    if (!FFileHelper::LoadFileToString(JsonText, *Path))
    {
        UE_LOG(LogTemp, Warning, TEXT("LivingWorldDirector: could not read %s; using baseline defaults."), *Path);
        return false;
    }

    TSharedPtr<FJsonObject> Root;
    const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonText);
    if (!FJsonSerializer::Deserialize(Reader, Root) || !Root.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("LivingWorldDirector: invalid world-life saturation contract."));
        return false;
    }

    BaselineTargetByChapter.Empty();
    const TSharedPtr<FJsonObject>* Targets = nullptr;
    if (Root->TryGetObjectField(TEXT("baseline_population_targets"), Targets) && Targets && Targets->IsValid())
    {
        for (const auto& Pair : (*Targets)->Values)
        {
            BaselineTargetByChapter.Add(FName(*Pair.Key), FMath::Clamp(static_cast<int32>(Pair.Value->AsNumber()), 0, 24));
        }
    }

    BaselineRolesByChapter.Empty();
    const TSharedPtr<FJsonObject>* Roles = nullptr;
    if (Root->TryGetObjectField(TEXT("population_roles"), Roles) && Roles && Roles->IsValid())
    {
        for (const auto& Pair : (*Roles)->Values)
        {
            TArray<FName> ParsedRoles;
            const TArray<TSharedPtr<FJsonValue>>* RoleValues = nullptr;
            if (Pair.Value.IsValid() && Pair.Value->TryGetArray(RoleValues) && RoleValues)
            {
                for (const TSharedPtr<FJsonValue>& RoleValue : *RoleValues)
                {
                    const FString RoleString = RoleValue.IsValid() ? RoleValue->AsString() : FString();
                    if (!RoleString.IsEmpty())
                    {
                        ParsedRoles.Add(FName(*RoleString));
                    }
                }
            }
            BaselineRolesByChapter.Add(FName(*Pair.Key), MoveTemp(ParsedRoles));
        }
    }

    const TSharedPtr<FJsonObject>* Density = nullptr;
    if (Root->TryGetObjectField(TEXT("density_profile"), Density) && Density && Density->IsValid())
    {
        double Value = 0.0;
        if ((*Density)->TryGetNumberField(TEXT("max_active_micro_events_near_player"), Value))
        {
            MaxActiveMicroEvents = FMath::Clamp(static_cast<int32>(Value), 1, 6);
        }
        if ((*Density)->TryGetNumberField(TEXT("min_seconds_between_event_starts"), Value))
        {
            MinSecondsBetweenEventStarts = FMath::Clamp(static_cast<float>(Value), 4.0f, 30.0f);
        }
        if ((*Density)->TryGetNumberField(TEXT("baseline_spawn_interval_seconds"), Value))
        {
            PopulationSpawnInterval = FMath::Clamp(static_cast<float>(Value), 0.25f, 2.0f);
        }
        if ((*Density)->TryGetNumberField(TEXT("baseline_inner_radius_cm"), Value))
        {
            PopulationInnerRadius = FMath::Clamp(static_cast<float>(Value), 500.0f, 1800.0f);
        }
        if ((*Density)->TryGetNumberField(TEXT("baseline_outer_radius_cm"), Value))
        {
            PopulationOuterRadius = FMath::Clamp(static_cast<float>(Value), PopulationInnerRadius + 200.0f, 4200.0f);
        }
        if ((*Density)->TryGetNumberField(TEXT("baseline_cull_radius_cm"), Value))
        {
            PopulationCullRadius = FMath::Clamp(static_cast<float>(Value), PopulationOuterRadius + 800.0f, 9000.0f);
        }
    }

    PopulationProfilesByChapter.Empty();
    const TSharedPtr<FJsonObject>* Profiles = nullptr;
    if (Root->TryGetObjectField(TEXT("chapter_density_profiles"), Profiles) && Profiles && Profiles->IsValid())
    {
        for (const auto& Pair : (*Profiles)->Values)
        {
            const TSharedPtr<FJsonObject> ProfileObject =
                Pair.Value.IsValid() ? Pair.Value->AsObject() : nullptr;
            if (!ProfileObject.IsValid())
            {
                continue;
            }

            FChapterPopulationProfile Profile;
            Profile.SpawnInterval = PopulationSpawnInterval;
            Profile.InnerRadius = PopulationInnerRadius;
            Profile.OuterRadius = PopulationOuterRadius;
            Profile.CullRadius = PopulationCullRadius;
            Profile.DangerPopulationFraction = 0.50f;

            double Value = 0.0;
            if (ProfileObject->TryGetNumberField(TEXT("spawn_interval_seconds"), Value))
            {
                Profile.SpawnInterval = FMath::Clamp(static_cast<float>(Value), 0.25f, 2.0f);
            }
            if (ProfileObject->TryGetNumberField(TEXT("baseline_inner_radius_cm"), Value))
            {
                Profile.InnerRadius = FMath::Clamp(static_cast<float>(Value), 500.0f, 1800.0f);
            }
            if (ProfileObject->TryGetNumberField(TEXT("baseline_outer_radius_cm"), Value))
            {
                Profile.OuterRadius = FMath::Clamp(
                    static_cast<float>(Value),
                    Profile.InnerRadius + 200.0f,
                    4200.0f);
            }
            if (ProfileObject->TryGetNumberField(TEXT("baseline_cull_radius_cm"), Value))
            {
                Profile.CullRadius = FMath::Clamp(
                    static_cast<float>(Value),
                    Profile.OuterRadius + 800.0f,
                    9000.0f);
            }
            if (ProfileObject->TryGetNumberField(TEXT("danger_population_fraction"), Value))
            {
                Profile.DangerPopulationFraction = FMath::Clamp(static_cast<float>(Value), 0.10f, 1.0f);
            }

            PopulationProfilesByChapter.Add(FName(*Pair.Key), Profile);
        }
    }

    return BaselineTargetByChapter.Num() > 0;
}

void ALivingWorldDirector::HandleChapterChanged(FName PreviousChapterId, FName NewChapterId)
{
    SynchronizeCommittedWorld();
}

void ALivingWorldDirector::HandleExperienceChanged(
    FName RouteId,
    FName EpisodeId,
    FName PlayableCharacterId)
{
    SynchronizeCommittedWorld();
}

void ALivingWorldDirector::HandleWorldCommitted(uint32 Revision)
{
    SynchronizeCommittedWorld();
}

bool ALivingWorldDirector::SynchronizeCommittedWorld()
{
    if (!QuestSubsystem)
    {
        return false;
    }

    if (!WorldRouter.IsValid())
    {
        WorldRouter = Cast<AChapterWorldRouter>(UGameplayStatics::GetActorOfClass(
            this, AChapterWorldRouter::StaticClass()));
        if (AChapterWorldRouter* Router = WorldRouter.Get())
        {
            Router->OnWorldCommitted.RemoveAll(this);
            Router->OnWorldCommitted.AddUObject(
                this, &ALivingWorldDirector::HandleWorldCommitted);
        }
    }

    AChapterWorldRouter* Router = WorldRouter.Get();
    if (!Router ||
        !Router->IsWorldCommitted(
            QuestSubsystem->GetCurrentChapterId(),
            QuestSubsystem->GetCurrentRouteId(),
            QuestSubsystem->GetCurrentEpisodeId()))
    {
        // Quest state can move ahead while the old world is still visible.
        // Never apply destination life/weather/context until geometry commits.
        return false;
    }

    if (AppliedWorldRevision != Router->GetWorldRevision())
    {
        ActiveChapterId = QuestSubsystem->GetCurrentChapterId();
        AppliedWorldRevision = Router->GetWorldRevision();
        ResetForCurrentChapter();
        UE_LOG(
            LogTemp,
            Display,
            TEXT("LivingWorldCommitSync: chapter=%s revision=%u"),
            *ActiveChapterId.ToString(),
            AppliedWorldRevision);
    }
    return true;
}

void ALivingWorldDirector::ResetForCurrentChapter()
{
    for (FActiveMicroEvent& Event : ActiveEvents)
    {
        for (TWeakObjectPtr<AActor>& ActorPtr : Event.Actors)
        {
            if (AActor* Actor = ActorPtr.Get())
            {
                if (AShireAmbientNPC* AmbientNPC = Cast<AShireAmbientNPC>(Actor))
                {
                    ReleaseAmbientNPCToPool(AmbientNPC);
                }
                else
                {
                    Actor->Destroy();
                }
            }
        }
    }
    ActiveEvents.Empty();

    for (TWeakObjectPtr<AShireAmbientNPC>& NPCPtr : BaselinePopulation)
    {
        if (AShireAmbientNPC* NPC = NPCPtr.Get())
        {
            ReleaseAmbientNPCToPool(NPC);
        }
    }
    BaselinePopulation.Empty();
    LastEventType = NAME_None;

    ApplyPopulationProfile();

    if (GetWorld())
    {
        const float Now = GetWorld()->GetTimeSeconds();
        NextEventTime = Now + 3.0f + Random.FRandRange(0.0f, 2.0f);
        NextPopulationSpawnTime = Now + FMath::Min(0.5f, PopulationSpawnInterval);
    }

    ApplyChapterWeatherContext();

    const int32* AuditTarget = BaselineTargetByChapter.Find(ActiveChapterId);
    UE_LOG(
        LogTemp,
        Display,
        TEXT("ShireChapterAudit: living-world chapter=%s baseline-target=%d spawn-interval=%.2f inner=%.0f outer=%.0f cull=%.0f danger-fraction=%.2f"),
        *ActiveChapterId.ToString(),
        AuditTarget ? *AuditTarget : 0,
        PopulationSpawnInterval,
        PopulationInnerRadius,
        PopulationOuterRadius,
        PopulationCullRadius,
        DangerPopulationFraction);
}

void ALivingWorldDirector::ApplyPopulationProfile()
{
    const FChapterPopulationProfile* Profile = PopulationProfilesByChapter.Find(ActiveChapterId);
    if (!Profile)
    {
        DangerPopulationFraction = 0.50f;
        return;
    }

    PopulationSpawnInterval = Profile->SpawnInterval;
    PopulationInnerRadius = Profile->InnerRadius;
    PopulationOuterRadius = Profile->OuterRadius;
    PopulationCullRadius = Profile->CullRadius;
    DangerPopulationFraction = Profile->DangerPopulationFraction;
}

void ALivingWorldDirector::ApplyChapterWeatherContext()
{
    UGameInstance* GI = GetGameInstance();
    UShireNPCContextSubsystem* Context =
        GI ? GI->GetSubsystem<UShireNPCContextSubsystem>() : nullptr;
    if (!Context)
    {
        return;
    }

    FName Weather = TEXT("CLEAR");
    if (ActiveChapterId == TEXT("P1C02"))
    {
        Weather = TEXT("RAIN");
    }
    else if (ActiveChapterId == TEXT("P1C05"))
    {
        Weather = TEXT("SNOW");
    }
    Context->SetWeatherState(Weather);
    UE_LOG(
        LogTemp,
        Display,
        TEXT("ShireChapterAudit: weather chapter=%s state=%s"),
        *ActiveChapterId.ToString(),
        *Weather.ToString());
}

bool ALivingWorldDirector::IsStoryDangerActive() const
{
    if (!QuestSubsystem)
    {
        return false;
    }

    UGameInstance* GI = GetGameInstance();
    UShireNPCContextSubsystem* Context =
        GI ? GI->GetSubsystem<UShireNPCContextSubsystem>() : nullptr;
    return Context && Context->IsDangerStateActive();
}

void ALivingWorldDirector::CleanupExpiredEvents()
{
    if (!GetWorld())
    {
        return;
    }

    const float Now = GetWorld()->GetTimeSeconds();
    APawn* Player = UGameplayStatics::GetPlayerPawn(this, 0);

    for (int32 Index = ActiveEvents.Num() - 1; Index >= 0; --Index)
    {
        bool bExpired = ActiveEvents[Index].ExpiresAt <= Now;

        for (TWeakObjectPtr<AActor>& ActorPtr : ActiveEvents[Index].Actors)
        {
            AActor* Actor = ActorPtr.Get();
            if (!Actor)
            {
                continue;
            }

            if (Player && FVector::DistSquared2D(Actor->GetActorLocation(), Player->GetActorLocation()) >
                FMath::Square(EventCullDistance))
            {
                bExpired = true;
            }
        }

        if (!bExpired)
        {
            continue;
        }

        for (TWeakObjectPtr<AActor>& ActorPtr : ActiveEvents[Index].Actors)
        {
            if (AActor* Actor = ActorPtr.Get())
            {
                if (AShireAmbientNPC* AmbientNPC = Cast<AShireAmbientNPC>(Actor))
                {
                    ReleaseAmbientNPCToPool(AmbientNPC);
                }
                else
                {
                    Actor->Destroy();
                }
            }
        }
        ActiveEvents.RemoveAt(Index);
    }
}

FName ALivingWorldDirector::ChooseEventType() const
{
    const TArray<FName>* Allowed = AllowedEventTypesByChapter.Find(ActiveChapterId);
    if (!Allowed || Allowed->Num() == 0)
    {
        return NAME_None;
    }

    TArray<FName> Candidates;
    for (const FName EventType : *Allowed)
    {
        if (EventType == LastEventType)
        {
            continue;
        }

        // Dead-city and danger-heavy chapters should never fabricate civilian life.
        if (ActiveChapterId == TEXT("P1C06") &&
            EventType != TEXT("PROP_MOTION") &&
            EventType != TEXT("DANGER_REACTION") &&
            EventType != TEXT("STORY_AFTERMATH"))
        {
            continue;
        }

        if (IsStoryDangerActive() &&
            (EventType == TEXT("MARKET_ACTIVITY") ||
             EventType == TEXT("SOCIAL_MOMENT") ||
             EventType == TEXT("WORK_ACTIVITY")))
        {
            continue;
        }

        Candidates.Add(EventType);
    }

    if (Candidates.Num() == 0)
    {
        return NAME_None;
    }

    return Candidates[Random.RandRange(0, Candidates.Num() - 1)];
}

FName ALivingWorldDirector::ResolveResidentRole(FName ChapterId) const
{
    if (ChapterId == TEXT("P1C02"))
    {
        return TEXT("BreeTownsperson");
    }
    if (ChapterId == TEXT("P1C04") || ChapterId == TEXT("P1C07"))
    {
        return TEXT("Elf");
    }
    return TEXT("Villager");
}

FName ALivingWorldDirector::ChooseBaselineRole() const
{
    const TArray<FName>* Roles = BaselineRolesByChapter.Find(ActiveChapterId);
    if (!Roles || Roles->Num() == 0)
    {
        return NAME_None;
    }
    return (*Roles)[Random.RandRange(0, Roles->Num() - 1)];
}

FName ALivingWorldDirector::ChooseBaselineProp(FName RoleName) const
{
    if (RoleName == TEXT("BreeCourier") || RoleName == TEXT("RoadWalker"))
    {
        return TEXT("Satchel");
    }
    if (RoleName == TEXT("FieldWorker") || RoleName == TEXT("Gardener"))
    {
        return Random.FRand() > 0.45f ? FName(TEXT("Basket")) : FName(TEXT("Crate"));
    }
    if (RoleName == TEXT("MarketVendor"))
    {
        return Random.FRand() > 0.50f ? FName(TEXT("Basket")) : FName(TEXT("Crate"));
    }
    if (RoleName == TEXT("PartyGuest") || RoleName == TEXT("InnGuest"))
    {
        return Random.FRand() > 0.35f ? FName(TEXT("Mug")) : NAME_None;
    }
    if (RoleName == TEXT("FerryWorker") || RoleName == TEXT("GateWorker") ||
        RoleName == TEXT("ElfAttendant") || RoleName == TEXT("ElfWarden"))
    {
        return Random.FRand() > 0.45f ? FName(TEXT("Lantern")) : NAME_None;
    }
    if (RoleName == TEXT("StableHand"))
    {
        return Random.FRand() > 0.50f ? FName(TEXT("Crate")) : FName(TEXT("Satchel"));
    }
    if (RoleName == TEXT("Elf") || RoleName == TEXT("ElfScholar"))
    {
        return Random.FRand() > 0.35f ? FName(TEXT("Book")) : NAME_None;
    }
    if (RoleName == TEXT("ElfArtisan") || RoleName == TEXT("ElfCraftsperson"))
    {
        return Random.FRand() > 0.55f ? FName(TEXT("Book")) : FName(TEXT("Lantern"));
    }
    if (RoleName == TEXT("BoatTender"))
    {
        return Random.FRand() > 0.55f ? FName(TEXT("Crate")) : FName(TEXT("Lantern"));
    }
    if (RoleName == TEXT("BreeTownsperson"))
    {
        const float Roll = Random.FRand();
        return Roll > 0.66f ? FName(TEXT("Basket")) :
            (Roll > 0.33f ? FName(TEXT("Mug")) : FName(TEXT("Satchel")));
    }
    if (RoleName == TEXT("Villager"))
    {
        const float Roll = Random.FRand();
        return Roll > 0.70f ? FName(TEXT("Basket")) :
            (Roll > 0.40f ? FName(TEXT("Crate")) : NAME_None);
    }
    return NAME_None;
}

FVector ALivingWorldDirector::ChoosePopulationOrigin()
{
    APawn* Player = UGameplayStatics::GetPlayerPawn(this, 0);
    if (!Player)
    {
        return FVector::ZeroVector;
    }

    const float Radius = Random.FRandRange(PopulationInnerRadius, PopulationOuterRadius);
    FVector Direction = FVector::ZeroVector;

    // Most baseline life appears in the forward/side travel corridor so crowd flow
    // reinforces route readability. A smaller share remains fully radial to avoid
    // turning the world into a single moving line.
    if (Random.FRand() < 0.72f)
    {
        const FVector Forward = Player->GetActorForwardVector().GetSafeNormal2D();
        const FVector Right = Player->GetActorRightVector().GetSafeNormal2D();
        Direction = (
            Forward * Random.FRandRange(0.35f, 1.0f) +
            Right * Random.FRandRange(-0.90f, 0.90f)).GetSafeNormal2D();
    }

    if (Direction.IsNearlyZero())
    {
        const float Angle = Random.FRandRange(0.0f, 2.0f * PI);
        Direction = FVector(FMath::Cos(Angle), FMath::Sin(Angle), 0.0f);
    }

    FVector Origin = Player->GetActorLocation() + Direction * Radius;
    Origin.Z = FMath::Max(Player->GetActorLocation().Z - 60.0f, 40.0f);
    return Origin;
}

AShireAmbientNPC* ALivingWorldDirector::AcquireAmbientNPC(const FVector& Location)
{
    while (AmbientNPCPool.Num() > 0)
    {
        TWeakObjectPtr<AShireAmbientNPC> CandidatePtr = AmbientNPCPool.Pop(false);
        if (AShireAmbientNPC* Candidate = CandidatePtr.Get())
        {
            Candidate->SetActorLocation(Location, false, nullptr, ETeleportType::TeleportPhysics);
            return Candidate;
        }
    }

    if (!GetWorld())
    {
        return nullptr;
    }

    FActorSpawnParameters SpawnParams;
    SpawnParams.SpawnCollisionHandlingOverride =
        ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButAlwaysSpawn;
    return GetWorld()->SpawnActor<AShireAmbientNPC>(
        Location, FRotator::ZeroRotator, SpawnParams);
}

void ALivingWorldDirector::ReleaseAmbientNPCToPool(AShireAmbientNPC* NPC)
{
    if (!NPC || NPC->IsPendingKillPending())
    {
        return;
    }

    if (AmbientNPCPool.Num() >= MaxAmbientNPCPoolSize)
    {
        NPC->Destroy();
        return;
    }

    NPC->DeactivateForLivingWorldPool();
    AmbientNPCPool.AddUnique(NPC);
}

void ALivingWorldDirector::CleanupBaselinePopulation()
{
    APawn* Player = UGameplayStatics::GetPlayerPawn(this, 0);
    for (int32 Index = BaselinePopulation.Num() - 1; Index >= 0; --Index)
    {
        AShireAmbientNPC* NPC = BaselinePopulation[Index].Get();
        if (!NPC)
        {
            BaselinePopulation.RemoveAt(Index);
            continue;
        }

        if (Player && FVector::DistSquared2D(NPC->GetActorLocation(), Player->GetActorLocation()) >
            FMath::Square(PopulationCullRadius))
        {
            ReleaseAmbientNPCToPool(NPC);
            BaselinePopulation.RemoveAt(Index);
        }
    }
}

void ALivingWorldDirector::MaintainBaselinePopulation()
{
    if (!GetWorld() || !QuestSubsystem || QuestSubsystem->GetCurrentRouteId() != TEXT("FrodoMain"))
    {
        return;
    }

    CleanupBaselinePopulation();

    const int32* TargetPtr = BaselineTargetByChapter.Find(ActiveChapterId);
    int32 Target = TargetPtr ? *TargetPtr : 0;

    // Story danger thins the baseline crowd instead of freezing the world outright.
    // This preserves activity while keeping threat readability and AI cost bounded.
    if (IsStoryDangerActive() && Target > 0)
    {
        Target = FMath::Max(1, FMath::RoundToInt(Target * DangerPopulationFraction));
    }

    if (Target <= 0 || BaselinePopulation.Num() >= Target)
    {
        return;
    }

    const float Now = GetWorld()->GetTimeSeconds();
    if (Now < NextPopulationSpawnTime)
    {
        return;
    }

    const FName RoleName = ChooseBaselineRole();
    if (RoleName == NAME_None)
    {
        return;
    }

    const FVector Origin = ChoosePopulationOrigin();
    if (Origin.IsNearlyZero())
    {
        return;
    }

    APawn* Player = UGameplayStatics::GetPlayerPawn(this, 0);
    const FVector TravelForward =
        Player ? Player->GetActorForwardVector().GetSafeNormal2D() : FVector::ForwardVector;
    const FVector TravelRight =
        Player ? Player->GetActorRightVector().GetSafeNormal2D() : FVector::RightVector;
    FVector TravelOffset =
        TravelForward * Random.FRandRange(260.0f, 620.0f) +
        TravelRight * Random.FRandRange(-260.0f, 260.0f);

    float Speed = Random.FRandRange(38.0f, 68.0f);
    float MinWait = Random.FRandRange(0.8f, 2.5f);
    float MaxWait = Random.FRandRange(3.0f, 6.5f);

    if (RoleName == TEXT("BreeCourier") || RoleName == TEXT("RoadWalker"))
    {
        Speed = Random.FRandRange(68.0f, 92.0f);
        MinWait = 0.2f;
        MaxWait = 1.4f;
        TravelOffset *= 1.45f;
    }
    else if (RoleName == TEXT("FieldWorker") || RoleName == TEXT("Gardener"))
    {
        Speed = Random.FRandRange(34.0f, 48.0f);
        TravelOffset *= 0.55f;
        MaxWait = Random.FRandRange(5.0f, 9.0f);
    }
    else if (RoleName == TEXT("MarketVendor") || RoleName == TEXT("InnGuest"))
    {
        Speed = Random.FRandRange(26.0f, 38.0f);
        TravelOffset *= 0.36f;
        MinWait = Random.FRandRange(2.5f, 4.0f);
        MaxWait = Random.FRandRange(6.0f, 10.0f);
    }
    else if (RoleName == TEXT("StableHand") || RoleName == TEXT("GateWorker"))
    {
        Speed = Random.FRandRange(38.0f, 54.0f);
        TravelOffset *= 0.62f;
        MinWait = Random.FRandRange(1.4f, 2.8f);
        MaxWait = Random.FRandRange(4.0f, 7.0f);
    }
    else if (RoleName == TEXT("Elf") || RoleName == TEXT("ElfScholar") ||
             RoleName == TEXT("ElfArtisan") || RoleName == TEXT("ElfAttendant") ||
             RoleName == TEXT("ElfWarden") || RoleName == TEXT("ElfCraftsperson") ||
             RoleName == TEXT("BoatTender"))
    {
        Speed = RoleName == TEXT("ElfWarden")
            ? Random.FRandRange(52.0f, 66.0f)
            : Random.FRandRange(40.0f, 56.0f);
        MinWait = RoleName == TEXT("BoatTender") ? 1.0f : 1.8f;
        MaxWait = (RoleName == TEXT("ElfScholar") || RoleName == TEXT("ElfCraftsperson"))
            ? Random.FRandRange(5.0f, 8.0f)
            : Random.FRandRange(4.0f, 6.5f);
        if (RoleName == TEXT("ElfScholar") || RoleName == TEXT("ElfCraftsperson"))
        {
            TravelOffset *= 0.55f;
        }
    }
    else if (RoleName == TEXT("Bird"))
    {
        Speed = Random.FRandRange(110.0f, 150.0f);
        MinWait = 0.0f;
        MaxWait = 0.4f;
        TravelOffset *= 2.1f;
    }
    else if (RoleName == TEXT("Rabbit"))
    {
        Speed = Random.FRandRange(78.0f, 108.0f);
        MinWait = 0.8f;
        MaxWait = 2.8f;
        TravelOffset *= 0.72f;
    }
    else if (RoleName == TEXT("Butterfly"))
    {
        Speed = Random.FRandRange(30.0f, 48.0f);
        MinWait = 0.2f;
        MaxWait = 1.0f;
        TravelOffset *= 0.48f;
    }

    if (AShireAmbientNPC* NPC = SpawnAmbientActor(
        Origin,
        RoleName,
        ChooseBaselineProp(RoleName),
        TravelOffset,
        Speed,
        MinWait,
        MaxWait))
    {
        NPC->Tags.AddUnique(TEXT("LivingWorldBaseline"));
        BaselinePopulation.Add(NPC);
    }

    NextPopulationSpawnTime = Now + PopulationSpawnInterval;
}

FVector ALivingWorldDirector::ChooseEventOrigin(float MinRadius, float MaxRadius)
{
    APawn* Player = UGameplayStatics::GetPlayerPawn(this, 0);
    if (!Player)
    {
        return FVector::ZeroVector;
    }

    const float Angle = Random.FRandRange(0.0f, 2.0f * PI);
    const float Radius = Random.FRandRange(MinRadius, MaxRadius);
    const FVector Offset(FMath::Cos(Angle) * Radius, FMath::Sin(Angle) * Radius, 0.0f);
    FVector Origin = Player->GetActorLocation() + Offset;
    Origin.Z = FMath::Max(Origin.Z - 60.0f, 40.0f);
    return Origin;
}

bool ALivingWorldDirector::ResolveGroundedAmbientPoint(
    const FVector& Candidate,
    FVector& OutGroundedPoint) const
{
    if (!GetWorld())
    {
        return false;
    }

    const FVector TraceStart = Candidate + FVector(0.0f, 0.0f, 900.0f);
    const FVector TraceEnd = Candidate - FVector(0.0f, 0.0f, 2200.0f);
    FCollisionQueryParams QueryParams(FName(TEXT("LivingWorldGroundProbe")), false, this);
    if (APawn* Player = UGameplayStatics::GetPlayerPawn(this, 0))
    {
        QueryParams.AddIgnoredActor(Player);
    }

    FHitResult GroundHit;
    if (!GetWorld()->LineTraceSingleByChannel(
            GroundHit,
            TraceStart,
            TraceEnd,
            ECC_Visibility,
            QueryParams) ||
        !GroundHit.bBlockingHit)
    {
        return false;
    }

    OutGroundedPoint = Candidate;
    OutGroundedPoint.Z = GroundHit.ImpactPoint.Z + 2.0f;
    return true;
}

AShireAmbientNPC* ALivingWorldDirector::SpawnAmbientActor(
    const FVector& Location,
    FName RoutineRole,
    FName ActivityProp,
    const FVector& TravelOffset,
    float Speed,
    float MinWait,
    float MaxWait)
{
    if (!GetWorld())
    {
        return nullptr;
    }

    const bool bGroundBound =
        RoutineRole != TEXT("Bird") &&
        RoutineRole != TEXT("Butterfly");

    FVector SpawnLocation = Location;
    FVector RoutineEnd = Location + TravelOffset;
    if (bGroundBound)
    {
        if (!ResolveGroundedAmbientPoint(Location, SpawnLocation))
        {
            UE_LOG(
                LogTemp,
                Verbose,
                TEXT("LivingWorldPlacement: rejected role=%s reason=no-ground"),
                *RoutineRole.ToString());
            return nullptr;
        }

        FVector GroundedRoutineEnd = FVector::ZeroVector;
        if (ResolveGroundedAmbientPoint(RoutineEnd, GroundedRoutineEnd))
        {
            RoutineEnd = GroundedRoutineEnd;
        }
        else
        {
            // Do not send a ground-bound ambient actor toward an unproven endpoint.
            RoutineEnd = SpawnLocation;
        }
    }

    AShireAmbientNPC* NPC = AcquireAmbientNPC(SpawnLocation);
    if (!NPC)
    {
        return nullptr;
    }

    NPC->Tags.AddUnique(TEXT("LivingWorldEphemeral"));
    NPC->Tags.AddUnique(TEXT("LivingWorldManaged"));
    NPC->ConfigureLivingWorldRoutine(
        SpawnLocation,
        RoutineEnd,
        RoutineRole,
        ActivityProp,
        Speed,
        MinWait,
        MaxWait);
    return NPC;
}

AWorldAmbientMotionActor* ALivingWorldDirector::SpawnAmbientMotionActor(
    UStaticMesh* Mesh,
    const FVector& Location,
    const FRotator& Rotation,
    const FVector& Scale,
    FName MotionMode,
    float Amplitude,
    float Speed)
{
    if (!GetWorld() || !Mesh)
    {
        return nullptr;
    }

    FActorSpawnParameters Params;
    Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    AWorldAmbientMotionActor* Actor = GetWorld()->SpawnActor<AWorldAmbientMotionActor>(
        Location, Rotation, Params);
    if (!Actor)
    {
        return nullptr;
    }

    EWorldAmbientMotionMode Mode = EWorldAmbientMotionMode::Sway;
    if (MotionMode == TEXT("BOB"))
    {
        Mode = EWorldAmbientMotionMode::Bob;
    }
    else if (MotionMode == TEXT("ROTATE"))
    {
        Mode = EWorldAmbientMotionMode::Rotate;
    }
    else if (MotionMode == TEXT("SHIVER"))
    {
        Mode = EWorldAmbientMotionMode::Shiver;
    }

    Actor->Tags.AddUnique(TEXT("LivingWorldEphemeral"));
    Actor->Configure(Mesh, Mode, Amplitude, Speed, Scale, false);
    return Actor;
}

AShireWorldEventInteraction* ALivingWorldDirector::SpawnPlayerInteraction(
    FName EventId,
    FName EventType,
    const FVector& Origin)
{
    if (!GetWorld() || IsStoryDangerActive())
    {
        return nullptr;
    }

    FText Prompt;
    FText Response;
    if (EventType == TEXT("WORK_ACTIVITY"))
    {
        Prompt = FText::FromString(TEXT("Help with the passing work."));
        Response = ActiveChapterId == TEXT("P1C04")
            ? FText::FromString(TEXT("You steady the books and leave the quiet work to continue."))
            : FText::FromString(TEXT("You lend a hand for a moment, then return to the road."));
    }
    else if (EventType == TEXT("MARKET_ACTIVITY"))
    {
        Prompt = FText::FromString(TEXT("Pause by the small exchange."));
        Response = FText::FromString(TEXT("A few ordinary words pass between neighbors. Nothing about the main road changes."));
    }
    else if (EventType == TEXT("SOCIAL_MOMENT"))
    {
        Prompt = FText::FromString(TEXT("Return the greeting."));
        Response = FText::FromString(TEXT("The brief greeting makes the place feel lived in, then the moment passes."));
    }
    else if (EventType == TEXT("TRAVELER_PASSING"))
    {
        Prompt = FText::FromString(TEXT("Acknowledge the passing traveler."));
        Response = FText::FromString(TEXT("You exchange a short road courtesy and let the traveler continue."));
    }
    else
    {
        return nullptr;
    }

    FActorSpawnParameters Params;
    Params.SpawnCollisionHandlingOverride =
        ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButAlwaysSpawn;
    AShireWorldEventInteraction* Interaction =
        GetWorld()->SpawnActor<AShireWorldEventInteraction>(
            Origin + FVector(70.0f, -70.0f, 0.0f),
            FRotator::ZeroRotator,
            Params);
    if (!Interaction)
    {
        return nullptr;
    }

    Interaction->Tags.AddUnique(TEXT("LivingWorldEphemeral"));
    Interaction->ConfigureInteraction(
        EventId,
        EventType,
        ActiveChapterId,
        Prompt,
        Response,
        true);
    return Interaction;
}

bool ALivingWorldDirector::SpawnEvent(FName EventType, FActiveMicroEvent& OutEvent)
{
    if (!GetWorld())
    {
        return false;
    }

    const FVector Origin = ChooseEventOrigin();
    if (Origin.IsNearlyZero())
    {
        return false;
    }

    OutEvent.EventType = EventType;
    OutEvent.EventId = FName(*FString::Printf(
        TEXT("%s_%s_%d"),
        *ActiveChapterId.ToString(),
        *EventType.ToString(),
        Random.RandRange(1000, 9999)));

    const FName ResidentRole = ResolveResidentRole(ActiveChapterId);
    float Duration = 12.0f;

    if (EventType == TEXT("WORK_ACTIVITY"))
    {
        if (ActiveChapterId != TEXT("P1C01") &&
            ActiveChapterId != TEXT("P1C02") &&
            ActiveChapterId != TEXT("P1C04"))
        {
            return false;
        }

        const FName Prop = ActiveChapterId == TEXT("P1C04") ? FName(TEXT("Book")) :
            (Random.FRand() > 0.5f ? FName(TEXT("Basket")) : FName(TEXT("Crate")));
        if (AShireAmbientNPC* NPC = SpawnAmbientActor(
            Origin, ResidentRole, Prop, FVector(220.0f, 70.0f, 0.0f), 46.0f, 2.0f, 5.0f))
        {
            OutEvent.Actors.Add(NPC);
        }
        Duration = 16.0f;
    }
    else if (EventType == TEXT("TRAVELER_PASSING"))
    {
        if (ActiveChapterId != TEXT("P1C01") && ActiveChapterId != TEXT("P1C02"))
        {
            return false;
        }

        const FName TravelerRole = ActiveChapterId == TEXT("P1C02")
            ? FName(TEXT("BreeTownsperson")) : FName(TEXT("Villager"));
        if (AShireAmbientNPC* NPC = SpawnAmbientActor(
            Origin, TravelerRole, TEXT("Satchel"), FVector(650.0f, Random.FRandRange(-180.0f, 180.0f), 0.0f),
            72.0f, 0.3f, 1.0f))
        {
            OutEvent.Actors.Add(NPC);
        }
        Duration = 18.0f;
    }
    else if (EventType == TEXT("MARKET_ACTIVITY"))
    {
        if (ActiveChapterId != TEXT("P1C01") && ActiveChapterId != TEXT("P1C02"))
        {
            return false;
        }

        AShireAmbientNPC* Seller = SpawnAmbientActor(
            Origin, ResidentRole, TEXT("Crate"), FVector(80.0f, 30.0f, 0.0f), 38.0f, 3.0f, 6.0f);
        AShireAmbientNPC* Buyer = SpawnAmbientActor(
            Origin + FVector(90.0f, 70.0f, 0.0f), ResidentRole, TEXT("Basket"),
            FVector(-70.0f, -35.0f, 0.0f), 42.0f, 2.5f, 5.0f);
        if (Seller) OutEvent.Actors.Add(Seller);
        if (Buyer) OutEvent.Actors.Add(Buyer);
        Duration = 18.0f;
    }
    else if (EventType == TEXT("SOCIAL_MOMENT"))
    {
        if (ActiveChapterId == TEXT("P1C03") || ActiveChapterId == TEXT("P1C05") ||
            ActiveChapterId == TEXT("P1C06") || ActiveChapterId == TEXT("P1C08"))
        {
            return false;
        }

        AShireAmbientNPC* First = SpawnAmbientActor(
            Origin, ResidentRole, NAME_None, FVector(110.0f, 40.0f, 0.0f), 38.0f, 2.0f, 4.0f);
        AShireAmbientNPC* Second = SpawnAmbientActor(
            Origin + FVector(110.0f, 70.0f, 0.0f), ResidentRole, TEXT("Mug"),
            FVector(-90.0f, -30.0f, 0.0f), 36.0f, 2.0f, 4.0f);
        if (First) OutEvent.Actors.Add(First);
        if (Second) OutEvent.Actors.Add(Second);
        Duration = 14.0f;
    }
    else if (EventType == TEXT("FAUNA"))
    {
        if (ActiveChapterId == TEXT("P1C05") || ActiveChapterId == TEXT("P1C06"))
        {
            return false;
        }

        const bool bWoodlandChapter =
            ActiveChapterId == TEXT("P1C01") ||
            ActiveChapterId == TEXT("P1C02") ||
            ActiveChapterId == TEXT("P1C04") ||
            ActiveChapterId == TEXT("P1C07");
        const bool bButterflyChapter =
            ActiveChapterId == TEXT("P1C01") ||
            ActiveChapterId == TEXT("P1C04") ||
            ActiveChapterId == TEXT("P1C07");

        const FVector SkyOrigin = Origin + FVector(0.0f, 0.0f, Random.FRandRange(360.0f, 620.0f));
        const int32 BirdCount = bWoodlandChapter ? 2 : 3;
        for (int32 Index = 0; Index < BirdCount; ++Index)
        {
            const FVector BirdOrigin = SkyOrigin + FVector(0.0f, Index * 110.0f - 70.0f, Index * 24.0f);
            if (AShireAmbientNPC* Bird = SpawnAmbientActor(
                BirdOrigin, TEXT("Bird"), NAME_None,
                FVector(720.0f, Random.FRandRange(-380.0f, 380.0f), Random.FRandRange(-45.0f, 90.0f)),
                148.0f + Index * 14.0f, 0.0f, 0.0f))
            {
                Bird->bCanNoticePlayer = false;
                OutEvent.Actors.Add(Bird);
            }
        }

        if (bWoodlandChapter && Random.FRand() > 0.35f)
        {
            const FVector RabbitOrigin = Origin + FVector(
                Random.FRandRange(-120.0f, 120.0f),
                Random.FRandRange(-120.0f, 120.0f),
                0.0f);
            if (AShireAmbientNPC* Rabbit = SpawnAmbientActor(
                RabbitOrigin, TEXT("Rabbit"), NAME_None,
                FVector(Random.FRandRange(260.0f, 440.0f), Random.FRandRange(-220.0f, 220.0f), 0.0f),
                Random.FRandRange(78.0f, 105.0f), 0.8f, 2.4f))
            {
                Rabbit->bCanNoticePlayer = false;
                OutEvent.Actors.Add(Rabbit);
            }
        }

        if (bButterflyChapter)
        {
            const FVector ButterflyOrigin = Origin + FVector(0.0f, 0.0f, Random.FRandRange(70.0f, 140.0f));
            for (int32 Index = 0; Index < 2; ++Index)
            {
                if (AShireAmbientNPC* Butterfly = SpawnAmbientActor(
                    ButterflyOrigin + FVector(0.0f, Index * 55.0f, Index * 18.0f),
                    TEXT("Butterfly"), NAME_None,
                    FVector(Random.FRandRange(260.0f, 420.0f), Random.FRandRange(-190.0f, 190.0f),
                        Random.FRandRange(-30.0f, 70.0f)),
                    Random.FRandRange(65.0f, 92.0f), 0.0f, 0.0f))
                {
                    Butterfly->bCanNoticePlayer = false;
                    OutEvent.Actors.Add(Butterfly);
                }
            }
        }

        Duration = 14.0f;
    }
    else if (EventType == TEXT("PROP_MOTION"))
    {
        UStaticMesh* MotionMesh = nullptr;
        FName MotionMode = TEXT("SWAY");
        float Amplitude = 4.0f;
        float Speed = 0.8f;
        FVector Scale(0.72f);

        if (ActiveChapterId == TEXT("P1C01"))
        {
            MotionMesh = Cast<UStaticMesh>(FSoftObjectPath(TEXT("/Game/Production/World/Shire/SM_ShLantern.SM_ShLantern")).ResolveObject());
            Amplitude = 5.0f;
            Speed = 0.70f;
        }
        else if (ActiveChapterId == TEXT("P1C02"))
        {
            MotionMesh = Cast<UStaticMesh>(FSoftObjectPath(TEXT("/Game/Production/World/Bree/SM_BreeInnSign.SM_BreeInnSign")).ResolveObject());
            Amplitude = 7.0f;
            Speed = 0.95f;
            Scale = FVector(0.64f);
        }
        else if (ActiveChapterId == TEXT("P1C03"))
        {
            MotionMesh = Cast<UStaticMesh>(FSoftObjectPath(TEXT("/Game/Production/World/Common/SM_CommonFallenLog.SM_CommonFallenLog")).ResolveObject());
            MotionMode = TEXT("SHIVER");
            Amplitude = 2.4f;
            Speed = 1.4f;
            Scale = FVector(0.60f);
        }
        else if (ActiveChapterId == TEXT("P1C04"))
        {
            MotionMesh = Cast<UStaticMesh>(FSoftObjectPath(TEXT("/Game/Production/World/Rivendell/SM_RivendellLantern.SM_RivendellLantern")).ResolveObject());
            Amplitude = 4.0f;
            Speed = 0.58f;
        }
        else if (ActiveChapterId == TEXT("P1C05"))
        {
            MotionMesh = Cast<UStaticMesh>(FSoftObjectPath(TEXT("/Game/Production/World/Road/SM_RoadSnowMarker.SM_RoadSnowMarker")).ResolveObject());
            MotionMode = TEXT("SHIVER");
            Amplitude = 3.8f;
            Speed = 1.9f;
            Scale = FVector(0.70f);
        }
        else if (ActiveChapterId == TEXT("P1C06"))
        {
            MotionMesh = Random.FRand() > 0.45f
                ? Cast<UStaticMesh>(FSoftObjectPath(TEXT("/Game/Production/World/Moria/SM_MoriaChainAnchor.SM_MoriaChainAnchor")).ResolveObject())
                : Cast<UStaticMesh>(FSoftObjectPath(TEXT("/Game/Production/World/Moria/SM_MoriaDebrisCluster.SM_MoriaDebrisCluster")).ResolveObject());
            MotionMode = TEXT("SHIVER");
            Amplitude = 2.2f;
            Speed = 1.15f;
            Scale = FVector(0.62f);
        }
        else if (ActiveChapterId == TEXT("P1C07"))
        {
            MotionMesh = Cast<UStaticMesh>(FSoftObjectPath(TEXT("/Game/Production/World/Lothlorien/SM_LorienLeafLantern.SM_LorienLeafLantern")).ResolveObject());
            MotionMode = TEXT("BOB");
            Amplitude = 8.0f;
            Speed = 0.52f;
            Scale = FVector(0.68f);
        }
        else if (ActiveChapterId == TEXT("P1C08"))
        {
            MotionMesh = Cast<UStaticMesh>(FSoftObjectPath(TEXT("/Game/Production/World/Anduin/SM_AnduinRiverMarker.SM_AnduinRiverMarker")).ResolveObject());
            MotionMode = TEXT("SWAY");
            Amplitude = 5.5f;
            Speed = 0.72f;
            Scale = FVector(0.66f);
        }

        if (AWorldAmbientMotionActor* Motion = SpawnAmbientMotionActor(
            MotionMesh,
            Origin,
            FRotator(0.0f, Random.FRandRange(-35.0f, 35.0f), 0.0f),
            Scale,
            MotionMode,
            Amplitude,
            Speed))
        {
            if (ActiveChapterId == TEXT("P1C01"))
            {
                Motion->ConfigureGlow(FLinearColor(1.0f, 0.48f, 0.16f), 180.0f, 210.0f);
            }
            else if (ActiveChapterId == TEXT("P1C02"))
            {
                Motion->ConfigureGlow(FLinearColor(1.0f, 0.34f, 0.10f), 150.0f, 190.0f);
            }
            else if (ActiveChapterId == TEXT("P1C04"))
            {
                Motion->ConfigureGlow(FLinearColor(0.72f, 0.84f, 1.0f), 170.0f, 230.0f);
            }
            else if (ActiveChapterId == TEXT("P1C06"))
            {
                Motion->ConfigureGlow(FLinearColor(1.0f, 0.20f, 0.05f), 120.0f, 175.0f);
            }
            else if (ActiveChapterId == TEXT("P1C07"))
            {
                Motion->ConfigureGlow(FLinearColor(1.0f, 0.72f, 0.22f), 210.0f, 260.0f);
            }

            OutEvent.Actors.Add(Motion);
            Duration = ActiveChapterId == TEXT("P1C06") ? 10.0f : 18.0f;
        }
    }
    else if (EventType == TEXT("WEATHER_REACTION"))
    {
        UGameInstance* GI = GetGameInstance();
        UShireNPCContextSubsystem* Context =
            GI ? GI->GetSubsystem<UShireNPCContextSubsystem>() : nullptr;
        if (Context)
        {
            if (ActiveChapterId == TEXT("P1C05"))
            {
                Context->SetWeatherState(TEXT("SNOW"));
            }
            else if (ActiveChapterId == TEXT("P1C02"))
            {
                Context->SetWeatherState(TEXT("RAIN"));
            }
        }
        return false;
    }
    else if (EventType == TEXT("DANGER_REACTION"))
    {
        // Caradhras danger is authored through storm/group traversal, not invented
        // resident scatter. Moria remains dead-city threat/aftermath only.
        if (ActiveChapterId == TEXT("P1C05"))
        {
            return false;
        }

        if (ActiveChapterId == TEXT("P1C06"))
        {
            UStaticMesh* ThreatMotionMesh = Random.FRand() > 0.5f
                ? Cast<UStaticMesh>(FSoftObjectPath(TEXT("/Game/Production/World/Moria/SM_MoriaDebrisCluster.SM_MoriaDebrisCluster")).ResolveObject())
                : Cast<UStaticMesh>(FSoftObjectPath(TEXT("/Game/Production/World/Moria/SM_MoriaChainAnchor.SM_MoriaChainAnchor")).ResolveObject());
            if (AWorldAmbientMotionActor* Motion = SpawnAmbientMotionActor(
                ThreatMotionMesh,
                Origin,
                FRotator(0.0f, Random.FRandRange(-30.0f, 30.0f), 0.0f),
                FVector(0.60f),
                TEXT("SHIVER"),
                3.2f,
                1.55f))
            {
                OutEvent.Actors.Add(Motion);
            }
            Duration = 8.0f;
        }
        else if (ActiveChapterId == TEXT("P1C03") || ActiveChapterId == TEXT("P1C08"))
        {
            const FVector SkyOrigin = Origin + FVector(0.0f, 0.0f, 420.0f);
            if (AShireAmbientNPC* Bird = SpawnAmbientActor(
                SkyOrigin, TEXT("Bird"), NAME_None,
                FVector(850.0f, Random.FRandRange(-420.0f, 420.0f), 90.0f),
                190.0f, 0.0f, 0.0f))
            {
                Bird->bCanNoticePlayer = false;
                OutEvent.Actors.Add(Bird);
            }
        }
        else
        {
            if (AShireAmbientNPC* NPC = SpawnAmbientActor(
                Origin, ResidentRole, TEXT("Satchel"),
                FVector(720.0f, Random.FRandRange(-320.0f, 320.0f), 0.0f),
                105.0f, 0.0f, 0.4f))
            {
                NPC->bCanNoticePlayer = false;
                OutEvent.Actors.Add(NPC);
            }
        }
        Duration = 10.0f;
    }
    else if (EventType == TEXT("STORY_AFTERMATH"))
    {
        if (ActiveChapterId == TEXT("P1C06"))
        {
            UStaticMesh* Debris = Cast<UStaticMesh>(FSoftObjectPath(TEXT("/Game/Production/World/Moria/SM_MoriaDebrisCluster.SM_MoriaDebrisCluster")).ResolveObject());
            UStaticMesh* Chain = Cast<UStaticMesh>(FSoftObjectPath(TEXT("/Game/Production/World/Moria/SM_MoriaChainAnchor.SM_MoriaChainAnchor")).ResolveObject());

            if (AWorldAmbientMotionActor* Motion = SpawnAmbientMotionActor(
                Random.FRand() > 0.5f ? Debris : Chain,
                Origin,
                FRotator(0.0f, Random.FRandRange(-20.0f, 20.0f), 0.0f),
                FVector(0.58f),
                TEXT("SHIVER"),
                2.6f,
                1.35f))
            {
                OutEvent.Actors.Add(Motion);
            }
            Duration = 9.0f;
        }
        else if (ActiveChapterId == TEXT("P1C08"))
        {
            const FVector SkyOrigin = Origin + FVector(0.0f, 0.0f, 520.0f);
            for (int32 Index = 0; Index < 2; ++Index)
            {
                if (AShireAmbientNPC* Bird = SpawnAmbientActor(
                    SkyOrigin + FVector(0.0f, Index * 130.0f, 35.0f * Index),
                    TEXT("Bird"), NAME_None,
                    FVector(620.0f, Index == 0 ? 260.0f : -260.0f, 50.0f),
                    130.0f, 0.0f, 0.0f))
                {
                    Bird->bCanNoticePlayer = false;
                    OutEvent.Actors.Add(Bird);
                }
            }
            Duration = 18.0f;
        }
        else
        {
            return false;
        }
    }
    else
    {
        return false;
    }

    if (OutEvent.Actors.Num() == 0)
    {
        return false;
    }

    if (AShireWorldEventInteraction* Interaction =
        SpawnPlayerInteraction(OutEvent.EventId, EventType, Origin))
    {
        OutEvent.Actors.Add(Interaction);
    }

    OutEvent.ExpiresAt = GetWorld()->GetTimeSeconds() + Duration;
    return true;
}

void ALivingWorldDirector::TryStartMicroEvent()
{
    if (!GetWorld() || !QuestSubsystem || ActiveEvents.Num() >= MaxActiveMicroEvents)
    {
        return;
    }

    // Parallel Isengard is deliberately story-authored rather than receiving Shire/Bree ambient events.
    if (QuestSubsystem->GetCurrentRouteId() != TEXT("FrodoMain"))
    {
        return;
    }

    const FName EventType = ChooseEventType();
    if (EventType == NAME_None)
    {
        return;
    }

    FActiveMicroEvent Event;
    if (SpawnEvent(EventType, Event))
    {
        LastEventType = EventType;
        ActiveEvents.Add(MoveTemp(Event));
    }
}

void ALivingWorldDirector::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    if (!GetWorld() || !QuestSubsystem || !SynchronizeCommittedWorld())
    {
        return;
    }

    CleanupExpiredEvents();
    MaintainBaselinePopulation();

    const float Now = GetWorld()->GetTimeSeconds();
    if (Now < NextEventTime)
    {
        return;
    }

    TryStartMicroEvent();
    NextEventTime = Now + MinSecondsBetweenEventStarts + Random.FRandRange(0.0f, 8.0f);
}
