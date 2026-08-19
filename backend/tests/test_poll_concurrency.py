import asyncio
import uuid

import httpx


BASE_URL = "http://127.0.0.1:8000"

# Change this if route 1 doesn't exist.
DESTINATION_ID = 1

DEPARTURE_TIME = "18:15"

NUMBER_OF_STUDENTS = 100


async def register_student(
    client: httpx.AsyncClient,
    index: int
):
    unique_id = uuid.uuid4().hex[:8]

    data = {
        "email": f"teststudent{index}_{unique_id}@busflow.test",
        "phone_number": f"90000{index:05d}",
        "password": "Test@12345",
        "student_id": f"TEST{index:03d}_{unique_id}",
        "course": "BTech",
        "branch": "CSE",
        "destination_id": DESTINATION_ID
    }

    response = await client.post(
        f"{BASE_URL}/auth/register",
        json=data
    )

    if response.status_code not in (200, 201):
        print(
            f"Registration failed for student {index}:",
            response.status_code,
            response.text
        )
        return None

    return {
        "email": data["email"],
        "password": data["password"]
    }


async def login_student(
    client: httpx.AsyncClient,
    student: dict
):
    response = await client.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": student["email"],
            "password": student["password"]
        }
    )

    if response.status_code != 200:
        print(
            "Login failed:",
            response.status_code,
            response.text
        )
        return None

    data = response.json()

    return data["access_token"]


async def create_poll(
    client: httpx.AsyncClient,
    manager_token: str
):
    response = await client.post(
        f"{BASE_URL}/polls/",
        headers={
            "Authorization":
                f"Bearer {manager_token}"
        },
        json={
            "departure_time": DEPARTURE_TIME
        }
    )

    if response.status_code not in (200, 201):
        raise RuntimeError(
            f"Poll creation failed: "
            f"{response.status_code} "
            f"{response.text}"
        )

    return response.json()["poll_id"]


async def submit_yes(
    client: httpx.AsyncClient,
    poll_id: str,
    token: str
):
    response = await client.post(
        f"{BASE_URL}/polls/{poll_id}/respond",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "response": "YES"
        }
    )

    return response.status_code, response.text


async def get_headcount(
    client: httpx.AsyncClient,
    poll_id: str,
    manager_token: str
):
    response = await client.get(
        f"{BASE_URL}/polls/{poll_id}/headcount",
        headers={
            "Authorization":
                f"Bearer {manager_token}"
        }
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Headcount request failed: "
            f"{response.status_code} "
            f"{response.text}"
        )

    return response.json()


async def main():

    print()
    print("======================================")
    print("BUSFLOW CONCURRENCY TEST")
    print("======================================")
    print()

    async with httpx.AsyncClient(
        timeout=30.0
    ) as client:

        # --------------------------------
        # STEP 1
        # Register 100 students
        # --------------------------------

        print(
            f"Registering "
            f"{NUMBER_OF_STUDENTS} students..."
        )

        registration_tasks = [
            register_student(
                client,
                i
            )
            for i in range(
                1,
                NUMBER_OF_STUDENTS + 1
            )
        ]

        students = await asyncio.gather(
            *registration_tasks
        )

        students = [
            student
            for student in students
            if student is not None
        ]

        print(
            f"Successfully registered: "
            f"{len(students)}"
        )

        if len(students) != NUMBER_OF_STUDENTS:
            raise RuntimeError(
                "Not all students registered."
            )

        # --------------------------------
        # STEP 2
        # Login all students
        # --------------------------------

        print()
        print("Logging in students...")

        login_tasks = [
            login_student(
                client,
                student
            )
            for student in students
        ]

        tokens = await asyncio.gather(
            *login_tasks
        )

        tokens = [
            token
            for token in tokens
            if token is not None
        ]

        print(
            f"Successfully logged in: "
            f"{len(tokens)}"
        )

        if len(tokens) != NUMBER_OF_STUDENTS:
            raise RuntimeError(
                "Not all students logged in."
            )

        # --------------------------------
        # STEP 3
        # Manager token
        # --------------------------------

        manager_token = input(
            "\nPaste manager JWT: "
        ).strip()

        if not manager_token:
            raise RuntimeError(
                "Manager token is required."
            )

        # --------------------------------
        # STEP 4
        # Create poll
        # --------------------------------

        print()
        print("Creating poll...")

        poll_id = await create_poll(
            client,
            manager_token
        )

        print(
            f"Poll created: {poll_id}"
        )

        # --------------------------------
        # STEP 5
        # 100 concurrent YES requests
        # --------------------------------

        print()
        print(
            "Sending 100 concurrent YES "
            "responses..."
        )

        tasks = [
            submit_yes(
                client,
                poll_id,
                token
            )
            for token in tokens
        ]

        results = await asyncio.gather(
            *tasks
        )

        successful = sum(
            1
            for status, _ in results
            if status == 200
        )

        failed = [
            result
            for result in results
            if result[0] != 200
        ]

        print()
        print(
            f"Successful requests: "
            f"{successful}"
        )

        print(
            f"Failed requests: "
            f"{len(failed)}"
        )

        if failed:
            print()
            print("Failed requests:")

            for status, body in failed[:10]:
                print(
                    status,
                    body
                )

        # --------------------------------
        # STEP 6
        # Check final headcount
        # --------------------------------

        print()
        print("Checking final headcount...")

        result = await get_headcount(
            client,
            poll_id,
            manager_token
        )

        print()
        print("Headcount response:")
        print(result)

        headcounts = result.get(
            "headcounts",
            {}
        )

        final_count = headcounts.get(
            str(DESTINATION_ID),
            0
        )

        print()
        print("======================================")
        print("RESULT")
        print("======================================")
        print(
            f"Expected headcount : "
            f"{NUMBER_OF_STUDENTS}"
        )
        print(
            f"Actual headcount   : "
            f"{final_count}"
        )

        if final_count == NUMBER_OF_STUDENTS:
            print()
            print(
                "✅ CONCURRENCY TEST PASSED"
            )
        else:
            print()
            print(
                "❌ CONCURRENCY TEST FAILED"
            )

        print("======================================")


if __name__ == "__main__":
    asyncio.run(main())