// Copyright 1998-2018 Epic Games, Inc. All Rights Reserved.

#include "VTC2018GameMode.h"
#include "VTC2018Character.h"
#include "UObject/ConstructorHelpers.h"

AVTC2018GameMode::AVTC2018GameMode()
{
	// set default pawn class to our Blueprinted character
	static ConstructorHelpers::FClassFinder<APawn> PlayerPawnBPClass(TEXT("/Game/ThirdPersonCPP/Blueprints/ThirdPersonCharacter"));
	if (PlayerPawnBPClass.Class != NULL)
	{
		DefaultPawnClass = PlayerPawnBPClass.Class;
	}
}
