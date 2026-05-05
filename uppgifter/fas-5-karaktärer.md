# Fas 5 — karaktärer som kommenterar

## Mål

Lägg till karaktärer som kommenterar spelets gång genom att anropa
Claudes API. Karaktärerna ska ha distinkta personligheter och
kommentera baserat på vad som faktiskt händer på brädet.

## Krav

- Minst tre karaktärer som användaren kan välja mellan. Personligheterna
  bestämmer ni själva.
- Karaktären ska åtminstone kommentera vid milstolpar (vinst, missade vinstläggen,
  blockerade hot)
- Karaktären ska ha tillgång till information om vad som händer i spelet,
  inte bara råa fakta. Det vill säga att karaktärens kommentarer ska
  vara relevanta för det som faktiskt sker (missade vinster, gafflar,
  blockerade hot, etc.)
- Det ska gå att välja "Ingen karaktär" — då görs inga API-anrop
- API-anropet ska inte frysa gränssnittet (svaret kan ta 1-2 sekunder)
- API-nyckeln ska läsas från miljövariabel `ANTHROPIC_API_KEY`,
  inte hårdkodas