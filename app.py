import asyncio
import json
import uuid
from src.CSLBP.common import decrypt, encrypt

HOST = "0.0.0.0"
PORT = 9999
PRE_SHARED_KEY = (
    "940fd2e68dcaf9bb9f8860d7fe069507bbd629f6db337a266d8dd2d9bae5c911"
    "a6c2ad70f96a54953d9f259b2296978b006d3439093d90276bb12ae432c30755"  # DONT SHARE THIS.
)


async def simulate_processing(task_data: dict) -> dict:
    await asyncio.sleep(0.1)  # demo
    return {
        "id": task_data["id"],
        "status": "finished",
        "result": {"echo": task_data.get("data", "No input")},
    }


async def process_task(task_request: dict, writer: asyncio.StreamWriter):
    task_id = task_request.get("id")
    try:
        processing_status = json.dumps({"id": task_id, "status": "processing"}).encode(
            "utf-8"
        )
        encrypted_status = encrypt(processing_status, PRE_SHARED_KEY)
        writer.write(len(encrypted_status).to_bytes(4, "big") + encrypted_status)
        await writer.drain()

        result = await simulate_processing(task_request)
        result_bytes = json.dumps(result).encode("utf-8")
        encrypted_result = encrypt(result_bytes, PRE_SHARED_KEY)
        writer.write(len(encrypted_result).to_bytes(4, "big") + encrypted_result)
        await writer.drain()

    except Exception as e:
        print(f"[Task {task_id}] Failed: {e}")


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info("peername")
    print(f"Connection from {addr}")
    try:
        while True:
            prefix = await reader.readexactly(4)
            msg_len = int.from_bytes(prefix, byteorder="big")
            encrypted = await reader.readexactly(msg_len)

            try:
                decrypted = decrypt(encrypted, PRE_SHARED_KEY)
                task_request = json.loads(decrypted.decode("utf-8"))
                task_id = task_request.get("id")

                if not task_id:
                    raise ValueError("Missing task ID")

                asyncio.create_task(process_task(task_request, writer))

            except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as e:
                print(f"[{addr[0]}:{addr[1]}] Invalid message: {e}")

            except Exception as e:
                print(f"[{addr[0]}:{addr[1]}] Error: {e}")

    except asyncio.IncompleteReadError:
        pass

    except:
        pass

    finally:
        print(f"Connection closed: {addr}")
        writer.close()
        await writer.wait_closed()


async def main():
    server = await asyncio.start_server(handle_client, HOST, PORT)
    addr = server.sockets[0].getsockname()
    print(f"CSLBP TCP Server listening on {addr}")
    async with server:
        try:
            await server.serve_forever()
        except KeyboardInterrupt:
            print("\nServer shutting down.")


if __name__ == "__main__":
    asyncio.run(main())
