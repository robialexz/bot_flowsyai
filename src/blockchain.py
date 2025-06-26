import asyncio
import json
import logging
from typing import Optional, Dict, Any, Callable, Awaitable

from websockets.client import connect
from websockets.exceptions import ConnectionClosed

logger = logging.getLogger(__name__)

class SolanaMonitor:
    """Monitors the Solana blockchain for transactions involving a specific token mint."""

    def __init__(
        self, 
        ws_url: str, 
        token_mint_address: str, 
        transaction_callback: Callable[[Dict[str, Any]], Awaitable[None]]
    ):
        self.ws_url = ws_url
        self.token_mint_address = token_mint_address
        self.transaction_callback = transaction_callback
        self.subscription_id: Optional[int] = None
        self.websocket = None

    async def start(self) -> None:
        """Starts the WebSocket connection and subscribes to logs."""
        while True:
            try:
                logger.info(f"Connecting to Solana WebSocket at {self.ws_url}...")
                async with connect(self.ws_url) as websocket:
                    self.websocket = websocket
                    await self._subscribe()
                    await self._listen()
            except (ConnectionClosed, ConnectionRefusedError, asyncio.TimeoutError) as e:
                logger.error(f"WebSocket connection error: {e}. Reconnecting in 10 seconds...")
                await asyncio.sleep(10)
            except Exception as e:
                logger.error(f"An unexpected error occurred in Solana monitor: {e}. Restarting...")
                await asyncio.sleep(10)

    async def _subscribe(self) -> None:
        """Subscribes to logs mentioning the token mint address."""
        subscribe_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "logsSubscribe",
            "params": [
                {"mentions": [self.token_mint_address]},
                {"commitment": "confirmed"}
            ]
        }
        await self.websocket.send(json.dumps(subscribe_message))
        response_str = await self.websocket.recv()
        response_data = json.loads(response_str)
        
        if 'error' in response_data:
            err_msg = response_data['error']['message']
            logger.error(f"Failed to subscribe to Solana logs: {err_msg}")
            raise ConnectionAbortedError(f"Subscription failed: {err_msg}")

        self.subscription_id = response_data.get('result')
        logger.info(f"Successfully subscribed to Solana logs for mint {self.token_mint_address}. Sub ID: {self.subscription_id}")

    async def _listen(self) -> None:
        """Listens for incoming messages and processes them."""
        while True:
            try:
                message = await self.websocket.recv()
                notification = json.loads(message)
                if notification.get('method') == 'logsNotification':
                    await self._process_log_notification(notification['params']['result'])
            except ConnectionClosed:
                logger.warning("WebSocket connection closed during listen. Will reconnect.")
                break # Exit listen loop to trigger reconnection

    async def _process_log_notification(self, log_result: Dict[str, Any]) -> None:
        """Processes a log notification to check for transfers and triggers the callback."""
        logs = log_result.get('value', {}).get('logs', [])
        signature = log_result.get('value', {}).get('signature')

        is_transfer = any("Instruction: Transfer" in log for log in logs)
        
        if is_transfer:
            logger.info(f"Confirmed token transfer involving {self.token_mint_address}. Signature: {signature}")
            await self.transaction_callback(log_result)

    async def stop(self) -> None:
        """Stops the monitor and unsubscribes from the logs."""
        if self.websocket and self.subscription_id is not None:
            try:
                unsubscribe_message = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "logsUnsubscribe",
                    "params": [self.subscription_id]
                }
                await self.websocket.send(json.dumps(unsubscribe_message))
                logger.info(f"Unsubscribed from Solana logs (Sub ID: {self.subscription_id}).")
            except Exception as e:
                logger.error(f"Error unsubscribing from Solana logs: {e}")
            finally:
                await self.websocket.close()
                self.websocket = None
                self.subscription_id = None