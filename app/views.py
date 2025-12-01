import time
import random
import requests
import threading
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import InsulinCalculationSerializer


class CalculateInsulinDoseView(APIView):
    def post(self, request):
        print("=== DJANGO: POST /api/calculate-insulin/ received ===")
        print("Request data:", request.data)

        # Валидация входных данных
        if 'insulin_calculation_id' not in request.data or 'patients' not in request.data:
            print("Error: Invalid request format")
            return Response({"error": "Invalid request format"}, status=status.HTTP_400_BAD_REQUEST)

        insulin_calculation_id = request.data['insulin_calculation_id']
        patients_data = request.data['patients']

        print(f"Processing calculation {insulin_calculation_id} with {len(patients_data)} patients")

        # Запускаем асинхронную обработку в отдельном потоке
        thread = threading.Thread(
            target=self.process_calculation_async,
            args=(insulin_calculation_id, patients_data)
        )
        thread.daemon = True
        thread.start()

        return Response({
            "message": "Calculation started",
            "calculation_id": insulin_calculation_id,
            "patients_count": len(patients_data)
        }, status=status.HTTP_202_ACCEPTED)

    def process_calculation_async(self, insulin_calculation_id, patients_data):
        """Асинхронная обработка расчета"""
        print(f"=== Starting async calculation for {insulin_calculation_id} ===")

        results = []

        # Обрабатываем каждого пациента
        for i, patient_data in enumerate(patients_data):
            print(f"Processing patient {i + 1}/{len(patients_data)}")

            # Валидация данных пациента
            serializer = InsulinCalculationSerializer(data=patient_data)
            if not serializer.is_valid():
                print(f"Validation error for patient {i + 1}: {serializer.errors}")
                continue  # Пропускаем некорректные данные

            data = serializer.validated_data

            # Имитация задержки 5-10 секунд
            delay_seconds = random.uniform(5, 10)
            print(f"Waiting {delay_seconds:.2f} seconds...")
            time.sleep(delay_seconds)

            # Расчет дозы инсулина
            calculated_dose = self.calculate_insulin_dose(
                data['current_glucose'],
                data['target_glucose'],
                data['sensitivity_coeff'],
                data['bread_units']
            )

            # Случайный результат (успех/неуспех)
            is_success = True # random.choice([True, False])
            print(f"Calculation result: {calculated_dose:.2f} (success: {is_success})")

            result = {
                'insulin_calculation_patient_id': patient_data['insulin_calculation_patient_id'],
                'patient_id': patient_data['patient_id'],
                'calculated_insulin': round(calculated_dose, 2) if is_success else 0,
                'status': 'success' if is_success else 'failed',
                'calculation_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            results.append(result)

        print(f"=== Calculation completed. Sending {len(results)} results back ===")

        # Отправка результатов обратно в основной сервис
        response_data = {
            'insulin_calculation_id': insulin_calculation_id,
            'results': results
        }

        # Отправляем результаты обратно
        self.send_results_to_go(response_data)

    def send_results_to_go(self, response_data):
        """Отправка результатов в Go сервис"""
        try:
            print("Sending results to Go service...")
            response = requests.post(
                'http://localhost:8080/api/insulin-calculations/result-dosages',
                json=response_data,
                headers={'Authorization': 'Bearer insulin123'},
                timeout=10
            )
            print(f"Go service response: {response.status_code}")
            if response.status_code == 200:
                print("Results sent successfully!")
            else:
                print(f"Error from Go: {response.text}")
        except Exception as e:
            print(f"Error sending result back: {e}")

    def calculate_insulin_dose(self, current_glucose, target_glucose, sensitivity_coeff, bread_units):
        """Расчет дозы болюсного инсулина по формуле 7"""
        correction_insulin = (current_glucose - target_glucose) * sensitivity_coeff
        food_insulin = 5 * sensitivity_coeff * bread_units
        total_dose = correction_insulin + food_insulin
        return max(0, total_dose)


class HealthCheckView(APIView):
    def get(self, request):
        return Response({
            "status": "healthy",
            "service": "Insulin Calculation Async Service",
            "timestamp": datetime.now().isoformat()
        })