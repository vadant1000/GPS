import grpc
import protos.phone_pb2 as phone_pb2
import protos.phone_pb2_grpc as phone_pb2_grpc
import time
import math
import random
from random_username.generate import generate_username

class GpsClient():
    def __init__(self):
        self.start_location = [55.751244, 37.618423] # начальные координаты объекта
        self.user_id = generate_username(1)[0] # use_id объекта
        self.option = 'get_one' # команда получения данных
        self.transfer_time = 0 # время которое будут передавться координаты в потоке
        self.algorithm = True # тип алгоритма вычисления

    @staticmethod
    def random_walk(start_location, max_step=0.001):
        """Случайное блуждание, координаты изменяются случайным образом."""
        x, y = start_location
        new_x = x + random.uniform(-max_step, max_step)  # Случайное изменение по широте
        new_y = y + random.uniform(-max_step, max_step)  # Случайное изменение по долготе
        return new_x, new_y


    @staticmethod
    def circular_movement(center_location, radius=0.001, speed=0.01, time_step=1):
        """Движение по кругу вокруг заданного центра."""
        x_center, y_center = center_location
        angle = time_step * speed  # Увеличиваем угол по времени
        new_x = x_center + radius * math.cos(angle)
        new_y = y_center + radius * math.sin(angle)
        return new_x, new_y


    def get_coordinates(self):
        if self.algorithm:
            calculation = GpsClient.random_walk
        else:
            calculation = GpsClient.circular_movement
        self.start_location[0], self.start_location[1] = calculation(self.start_location)
        telemetry = phone_pb2.Telemetry(user_id=self.user_id,
                                        location=phone_pb2.Telemetry.Location(
                                            latitude=self.start_location[0],
                                            longitude=self.start_location[1],
                                            timestamp=phone_pb2.Timestamp(
                                                seconds=int(time.time()),
                                                nanos=int(math.modf(time.time())[0]*1000000000))
                                        ))
        yield telemetry
        time.sleep(1)

    def transfer_coordinates(self):
        start_time = time.time()
        if self.algorithm:
            calculation = GpsClient.random_walk
        else:
            calculation = GpsClient.circular_movement
        while time.time() - start_time < client.transfer_time:
            self.start_location[0], self.start_location[1] = calculation(self.start_location)
            telemetry = phone_pb2.Telemetry(user_id=self.user_id,
                                            location=phone_pb2.Telemetry.Location(
                                                latitude=self.start_location[0],
                                                longitude=self.start_location[1],
                                                timestamp=phone_pb2.Timestamp(
                                                    seconds=int(time.time()),
                                                    nanos=int(math.modf(time.time())[0]*1000000000))
                                            ))
            yield telemetry
            time.sleep(1)

     
    
if __name__ == "__main__":

    """Клиент устанавливает соединение с сервером"""
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = phone_pb2_grpc.TelemetryServiceStub(channel)

        client = GpsClient()

        while True:
            if client.option == 'get_one':
                response_iterator = stub.SetTelemetryStream(client.get_coordinates())

            if client.option == 'start':
                response_iterator = stub.SetTelemetryStream(client.transfer_coordinates())

            for response in response_iterator:
                if response.HasField('get_one'):
                    client.option = 'get_one'
                elif response.HasField('start'):
                    client.transfer_time = response.start.duration
                    client.option = 'start'
                elif response.HasField('ack'):
                    client.algorithm = not client.algorithm
                    client.option = None

        
    
    
