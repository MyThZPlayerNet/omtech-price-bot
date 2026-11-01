# Token is entered locally, masked, and never printed or put in browser history.
$ErrorActionPreference = 'Stop'
$secureToken = Read-Host 'Wklej token z BotFather (wpis jest ukryty)' -AsSecureString
$pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureToken)
$plainToken = $null
try {
    $plainToken = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
    if ($plainToken -notmatch '^\d+:[A-Za-z0-9_-]+$') { throw 'invalid' }
    $apiBase = 'https://api.telegram.org/bot' + $plainToken
    $me = Invoke-RestMethod -Method Post -Uri ($apiBase + '/getMe')
    if (-not $me.ok) { throw 'invalid' }
    Write-Host ('Bot potwierdzony: @' + $me.result.username)
    $setupCode = '/setup_' + [Guid]::NewGuid().ToString('N').Substring(0, 10)
    Write-Host ('Otworz prywatna rozmowe ze swoim botem i wyslij: ' + $setupCode)
    Read-Host 'Po wyslaniu nacisnij Enter' | Out-Null
    $updates = Invoke-RestMethod -Method Post -Uri ($apiBase + '/getUpdates') -Body @{timeout=0; limit=100}
    if (-not $updates.ok) { throw 'invalid' }
    $matches = @($updates.result | Where-Object {
        $_.message.text -eq $setupCode -and $_.message.chat.type -eq 'private'
    })
    if ($matches.Count -eq 0) {
        Write-Host 'Nie znaleziono kodu. Wyslij go do wlasciwego bota i uruchom skrypt ponownie.'
        exit 1
    }
    $chatId = $matches[-1].message.chat.id
    Write-Host ('TELEGRAM_CHAT_ID = ' + $chatId)
    Write-Host 'Skopiuj te liczbe do GitHub Secrets. Token skopiuj bezposrednio z BotFather do drugiego sekretu.'
} catch {
    Write-Host 'Nie udalo sie odczytac czatu. Sprawdz token, siec, Start u bota i brak webhooka. Szczegoly bledu ukryto, aby nie ujawnic tokenu.'
    exit 1
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
    $plainToken = $null
    $apiBase = $null
    $secureToken.Dispose()
}
