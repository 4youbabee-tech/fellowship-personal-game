#include "LivingWorldDirector.h"

#include "ShireAmbientNPC.h"
#include "ShireNPCContextSubsystem.h"
#include "ShireQuestSubsystem.h"

#include "Dom/JsonObject.h"
#include "Engine/GameInstance.h"
#include "GameFramework/Pawn.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

ALivingWorldDirector::ALivingWorldDirector()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.TickInterval = 1.0f;
}

void ALivingWorldDirector::BeginPlay()
{
    Super::BeginPlay();

    Random.Initialize(7919);
    LoadEventContract();

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

    ResetForCurrentChapter();
}

void ALivingWorldDirector::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
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

void ALivingWorldDirector::HandleChapterChanged(FName PreviousChapterId, FName NewChapterId)
{
    ActiveChapterId = NewChapterId;
    ResetForCurrentChapter();
}

void ALivingWorldDirector::HandleExperienceChanged(
    FName RouteId,
    FName EpisodeId,
    FName PlayableCharacterId)
{
    if (QuestSubsystem)
    {
        ActiveChapterId = QuestSubsystem->GetCurrentChapterId();
    }
    ResetForCurrentChapter();
}

void ALivingWorldDirector::ResetForCurrentChapter()
{
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
    LastEventType = NAME_None;

    if (GetWorld())
    {
        NextEventTime = GetWorld()->GetTimeSeconds() + 5.0f + Random.FRandRange(0.0f, 4.0f);
    }

    ApplyChapterWeatherContext();
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
                Actor->Destroy();
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

AShireAmbientNPC* ALivingWorldDirector::SpawnAmbientActor(
    const FVector& Location,
    FName Role,
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

    AShireAmbientNPC* NPC = GetWorld()->SpawnActor<AShireAmbientNPC>(
        Location, FRotator::ZeroRotator);
    if (!NPC)
    {
        return nullptr;
    }

    NPC->Tags.AddUnique(TEXT("LivingWorldEphemeral"));
    NPC->RoutineRole = Role;
    NPC->ActivityPropType = ActivityProp;
    NPC->RoutinePointA = Location;
    NPC->RoutinePointB = Location + TravelOffset;
    NPC->WalkSpeed = Speed;
    NPC->MinWait = MinWait;
    NPC->MaxWait = MaxWait;
    return NPC;
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

        const FName Role = ActiveChapterId == TEXT("P1C02")
            ? FName(TEXT("BreeTownsperson")) : FName(TEXT("Villager"));
        if (AShireAmbientNPC* NPC = SpawnAmbientActor(
            Origin, Role, TEXT("Satchel"), FVector(650.0f, Random.FRandRange(-180.0f, 180.0f), 0.0f),
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
        if (ActiveChapterId == TEXT("P1C03") || ActiveChapterId == TEXT("P1C06") ||
            ActiveChapterId == TEXT("P1C08"))
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
        const FVector SkyOrigin = Origin + FVector(0.0f, 0.0f, Random.FRandRange(360.0f, 620.0f));
        for (int32 Index = 0; Index < 3; ++Index)
        {
            const FVector BirdOrigin = SkyOrigin + FVector(0.0f, Index * 90.0f - 90.0f, Index * 24.0f);
            if (AShireAmbientNPC* Bird = SpawnAmbientActor(
                BirdOrigin, TEXT("Bird"), NAME_None,
                FVector(700.0f, Random.FRandRange(-360.0f, 360.0f), Random.FRandRange(-40.0f, 80.0f)),
                145.0f + Index * 12.0f, 0.0f, 0.0f))
            {
                Bird->bCanNoticePlayer = false;
                OutEvent.Actors.Add(Bird);
            }
        }
        Duration = 12.0f;
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
        if (ActiveChapterId == TEXT("P1C06"))
        {
            return false;
        }

        if (ActiveChapterId == TEXT("P1C03") || ActiveChapterId == TEXT("P1C08"))
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
        if (ActiveChapterId == TEXT("P1C08"))
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

    if (!GetWorld() || !QuestSubsystem)
    {
        return;
    }

    CleanupExpiredEvents();

    if (QuestSubsystem->GetCurrentChapterId() != ActiveChapterId)
    {
        ActiveChapterId = QuestSubsystem->GetCurrentChapterId();
        ResetForCurrentChapter();
    }

    const float Now = GetWorld()->GetTimeSeconds();
    if (Now < NextEventTime)
    {
        return;
    }

    TryStartMicroEvent();
    NextEventTime = Now + MinSecondsBetweenEventStarts + Random.FRandRange(0.0f, 8.0f);
}
