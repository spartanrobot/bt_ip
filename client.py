import asyncio
from random import randrange as rr
from bleak import BleakScanner, BleakClient
import tkinter as tk

MODEL_NBR_UUID = "51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B"


# https://stackoverflow.com/a/47896365
class App(tk.Tk):

    def __init__(self, loop, interval=1 / 120):
        super().__init__()
        self.loop = loop
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.client = None
        self.tasks = []
        self.tasks.append(loop.create_task(self.conn("2C:CF:67:8B:0B:E4")))  # (await get_device()).address))

        self.label = tk.Label(self, text="Connecting...")
        self.label.pack()
        tk.Button(self, text="Shutdown Bot", command=self.do_things).pack()
        self.resizable(False, False)

        self.tasks.append(loop.create_task(self.updater(interval)))

    def do_things(self):
        self.tasks.append(loop.create_task(self.deleter()))

    async def deleter(self):
        await self.client.write_gatt_char(MODEL_NBR_UUID, b"\x0F")
        self.close()

    async def conn(self, address):
        print("Connecting to SpartanBot 1")
        self.client = BleakClient(address)
        await self.client.connect()
        ip_addr = await self.client.read_gatt_char(MODEL_NBR_UUID)
        self.label["text"] = "IP: " + ip_addr.decode("ascii")

    async def updater(self, interval):
        while True:
            self.update()
            await asyncio.sleep(interval)

    def close(self):
        self.tasks.append(loop.create_task(self.client.disconnect()))
        self.after(10, self._close)

    def _close(self):
        for task in self.tasks:
            task.cancel()
        self.loop.stop()
        self.destroy()


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
app = App(loop)
loop.run_forever()
loop.close()
