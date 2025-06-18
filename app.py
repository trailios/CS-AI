import asyncio
from src.CSLBP.common import decrypt

HOST = '0.0.0.0'
PORT = 9999
PRE_SHARED_KEY = (
    "940fd2e68dcaf9bb9f8860d7fe069507bbd629f6db337a266d8dd2d9bae5c911"
    "a6c2ad70f96a54953d9f259b2296978b006d3439093d90276bb12ae432c30755"
)

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info('peername')
    print(f"Connection from {addr}")
    try:
        while True:
            prefix = await reader.readexactly(4)
            msg_len = int.from_bytes(prefix, byteorder='big')
            encrypted = await reader.readexactly(msg_len)

            try:
                decrypted = decrypt(encrypted, PRE_SHARED_KEY)
                plaintext = decrypted.decode('utf-8')
                print(f"[{addr[0]}:{addr[1]}] {plaintext}")
            except UnicodeDecodeError:
                pass
            except Exception as e:
                pass
    except asyncio.IncompleteReadError:
        pass
    except:
        #excepting client clossed suddengly
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

if __name__ == '__main__':
    asyncio.run(main())
