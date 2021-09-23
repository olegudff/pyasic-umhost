import asyncio
import json


class APIError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f"{self.message}"
        else:
            return "Incorrect API parameters."


class BaseMinerAPI:
    def __init__(self, ip, port):
        self.port = port
        self.ip = ip

    async def multicommand(self, *commands: str):
        command = "+".join(commands)
        return await self.send_command(command)

    async def send_command(self, command, parameters: dict = None):
        # get reader and writer streams
        reader, writer = await asyncio.open_connection(self.ip, self.port)

        # create the command
        cmd = {"command": command}
        if parameters is not None:
            cmd["parameter"] = parameters

        # send the command
        writer.write(json.dumps(cmd).encode('utf-8'))
        await writer.drain()

        # instantiate data
        data = b""

        # loop to receive all the data
        while True:
            d = await reader.read(4096)
            if not d:
                break
            data += d

        data = json.loads(data.decode('utf-8')[:-1])

        # close the connection
        writer.close()
        await writer.wait_closed()

        # check if the data returned is correct or an error
        # if status isn't a key, it is a multicommand
        if "STATUS" not in data.keys():
            for key in data.keys():
                # make sure not to try to turn id into a dict
                if not key == "id":
                    # make sure they succeeded
                    if data[key][0]["STATUS"][0]["STATUS"] not in ["S", "I"]:
                        # this is an error
                        raise APIError(data["STATUS"][0]["Msg"])
        else:
            # make sure the command succeeded
            if data["STATUS"][0]["STATUS"] not in ("S", "I"):
                # this is an error
                raise APIError(data["STATUS"][0]["Msg"])

        # return the data
        return data
