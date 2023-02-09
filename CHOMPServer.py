import asyncio
import pickle
import websockets

class TableServer:
    def __init__(self):
        self.tables = {}
        self.load_tables_from_file()

    async def handle_request(self, websocket, path):
        request = await websocket.recv()
        request = request.split()
        command = request[0]
        request = " ".join(request[1:])

        if command == "store":
            table_name, entry = request.split("|")
            self.store_entry(table_name, entry)
            await websocket.send("Entry stored successfully.")
        elif command == "update":
            request = request.split("|")
            table_name, id, entry = request[1], int(request[2]), request[3:]
            self.update_entry(table_name, id, entry)
            await websocket.send("Entry updated successfully.")
        elif command == "delete":
            request = request.split("|")
            table_name, id = request[1], int(request[2])
            self.delete_entry(table_name, id)
            await websocket.send("Entry deleted successfully.")
        elif command == "list":
            table_name = request
            entries = self.list_entries(table_name)
            await websocket.send("\n".join(str(entry) for entry in entries))

    def store_entry(self, table_name, entry):
        if table_name not in self.tables:
            self.tables[table_name] = []
        self.tables[table_name].append(entry)
        self.save_tables_to_file()

    def update_entry(self, table_name, id, entry):
        self.tables[table_name][id] = entry
        self.save_tables_to_file()

    def delete_entry(self, table_name, id):
        self.tables[table_name][id] = None
        self.save_tables_to_file()

    def list_entries(self, table_name):
        return [entry for entry in self.tables[table_name] if entry is not None]

    def save_tables_to_file(self):
        with open("tables.pkl", "wb") as file:
            pickle.dump(self.tables, file)

    def load_tables_from_file(self):
        try:
            with open("tables.pkl", "rb") as file:
                self.tables = pickle.load(file)
        except FileNotFoundError:
            pass

server = TableServer()
start_server = websockets.serve(server.handle_request, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
