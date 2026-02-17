import pytest
from unittest.mock import AsyncMock, MagicMock
from handlers.registration import process_name
from states.registration import RegistrationStates
from aiogram.fsm.context import FSMContext

@pytest.mark.asyncio
async def test_process_name_handler():
    # Mock message and state
    message = MagicMock()
    message.text = "Ali"
    message.from_user.id = 12345
    message.answer = AsyncMock()
    
    state = MagicMock(spec=FSMContext)
    state.get_data = AsyncMock(return_value={'language': 'uz'})
    state.update_data = AsyncMock()
    state.set_state = AsyncMock()
    
    # Call handler
    await process_name(message, state)
    
    # Verify
    state.update_data.assert_called_with(name="Ali")
    state.set_state.assert_called_with(RegistrationStates.nickname)
    assert "nikney" in message.answer.call_args[0][0].lower()

@pytest.mark.asyncio
async def test_admin_check_logic():
    from handlers.admin import is_admin
    import os
    
    os.environ["ADMIN_ID"] = "999"
    assert is_admin(999) is True
    assert is_admin(111) is False
