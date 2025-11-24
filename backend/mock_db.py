import asyncio

class MockCursor:
    def __init__(self, data):
        self.data = data

    def sort(self, key, direction):
        reverse = direction == -1
        # Handle missing keys safely
        self.data.sort(key=lambda x: x.get(key, ""), reverse=reverse)
        return self

    async def to_list(self, length):
        return self.data[:length]

class MockCollection:
    def __init__(self, name):
        self.name = name
        self.data = []

    async def find_one(self, query, projection=None):
        for item in self.data:
            match = True
            for k, v in query.items():
                if item.get(k) != v:
                    match = False
                    break
            if match:
                # Return a copy to avoid accidental mutation if not intended
                return item.copy()
        return None

    async def insert_one(self, document):
        # Store a copy
        self.data.append(document.copy())
        return True

    async def update_one(self, query, update):
        # Find the actual item reference to update it
        target = None
        for item in self.data:
            match = True
            for k, v in query.items():
                if item.get(k) != v:
                    match = False
                    break
            if match:
                target = item
                break
        
        if target:
            if "$set" in update:
                for k, v in update["$set"].items():
                    target[k] = v
        return True

    async def delete_one(self, query):
        target = None
        for item in self.data:
            match = True
            for k, v in query.items():
                if item.get(k) != v:
                    match = False
                    break
            if match:
                target = item
                break
        
        if target:
            self.data.remove(target)
        return True

    def find(self, query, projection=None):
        result = []
        for item in self.data:
            match = True
            for k, v in query.items():
                if item.get(k) != v:
                    match = False
                    break
            if match:
                result.append(item.copy())
        return MockCursor(result)

class MockDB:
    def __init__(self):
        self.users = MockCollection("users")
        self.videos = MockCollection("videos")

    def __getitem__(self, name):
        return getattr(self, name)
