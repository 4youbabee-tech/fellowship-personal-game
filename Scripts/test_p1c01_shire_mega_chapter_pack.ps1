$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
$root = Split-Path -Parent $PSScriptRoot
$path = Join-Path $root "Data\P1C01ShireMegaChapterPackV1.json"
if(-not (Test-Path -LiteralPath $path -PathType Leaf)){ throw "P1C01_MEGA_PACK_MISSING" }
$j = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
if($j.runtime_chapter -ne "P1C01"){ throw "P1C01_MEGA_PACK_SCOPE_FAIL" }
if(@($j.production_cells).Count -lt 4){ throw "P1C01_MEGA_PACK_WORLD_CELLS_FAIL" }
if(@($j.character_contracts)[0].id -ne "FRODO"){ throw "P1C01_MEGA_PACK_FRODO_ORDER_FAIL" }
if(@($j.character_contracts)[1].id -ne "GANDALF"){ throw "P1C01_MEGA_PACK_GANDALF_ORDER_FAIL" }
if($j.living_shire.lifecycle_owner -ne "LivingWorldDirector"){ throw "P1C01_MEGA_PACK_LIVING_OWNER_FAIL" }
if($j.living_shire.context_owner -ne "ShireNPCContextSubsystem"){ throw "P1C01_MEGA_PACK_CONTEXT_OWNER_FAIL" }
if($j.gameplay.story_owner -ne "ShireQuestSubsystem"){ throw "P1C01_MEGA_PACK_STORY_OWNER_FAIL" }
if($j.audio.owner -ne "UShireAudioSubsystem"){ throw "P1C01_MEGA_PACK_AUDIO_OWNER_FAIL" }
if(-not ($j.material_surface.texture_rule -match "PNG/TGA")){ throw "P1C01_MEGA_PACK_TEXTURE_RULE_FAIL" }
if(-not (@($j.optimization.rules) -contains "FStreamableManager asynchronous heavy loading")){ throw "P1C01_MEGA_PACK_ASYNC_FAIL" }
if($j.gate_boundary.current_car -ne "P1C01-A_FRODO_SKELETAL_PRODUCTION"){ throw "P1C01_MEGA_PACK_GATE_DRIFT" }
if($j.gate_boundary.future_runtime_activation -ne "FORBIDDEN_UNTIL_PREDECESSOR_GATE_6_7"){ throw "P1C01_MEGA_PACK_FUTURE_GATE_FAIL" }
Write-Host "P1C01_MEGA_CHAPTER_PACK_PASS cells=$(@($j.production_cells).Count) gameplayWindows=$(@($j.gameplay.windows).Count) currentCar=$($j.gate_boundary.current_car)"
