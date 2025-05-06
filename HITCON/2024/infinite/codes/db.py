from datetime import datetime

from mysql.connector.aio import connect

from .model import Query, Bounty
from .config import config


class DBConnection:
    async def __aenter__(self):
        self.cnx = await connect(
            user=config["db"]["user"],
            password=config["db"]["password"],
            host=config["db"]["host"],
            database=config["db"]["database"],
            port=config["db"]["port"],
            autocommit=True,
            buffered=True,
        )
        self.cursor = await self.cnx.cursor()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.cursor.close()
        await self.cnx.close()


class DB:
    async def init(self):
        await self.create_tables()

    async def create_tables(self):
        async with DBConnection() as cnx:
            # create tables if not exists
            await cnx.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS element (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    english_name VARCHAR(255) NOT NULL UNIQUE,
                    symbol VARCHAR(255) NOT NULL
                )
                """
            )
            await cnx.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS recipe (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    product_english_name VARCHAR(255) NOT NULL,
                    material0 VARCHAR(255) NOT NULL,
                    material1 VARCHAR(255) NOT NULL,
                    material2 VARCHAR(255) NOT NULL,
                    material3 VARCHAR(255) NOT NULL,
                    material4 VARCHAR(255) NOT NULL,
                    material5 VARCHAR(255) NOT NULL,
                    material6 VARCHAR(255) NOT NULL,
                    material7 VARCHAR(255) NOT NULL
                )
                """
            )
            await cnx.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS team_element_unlocked (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    team_id INT NOT NULL,
                    english_name VARCHAR(255) NOT NULL
                )
                """
            )
            await cnx.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS bounty (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    team_id INT NOT NULL,
                    target_product VARCHAR(255), /* NULL means the team cleared its bounty */
                    length INT NOT NULL,
                    bounty_body TEXT NOT NULL,
                    is_submitted BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP(6)
                )
                """
            )
            await cnx.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS round (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    round_id INT NOT NULL UNIQUE,
                    end_at TIMESTAMP(6) DEFAULT NULL,
                    round_rank TEXT DEFAULT NULL
                )
                """
            )

            # placeholder round
            await cnx.cursor.execute(
                """
                INSERT INTO round (round_id) VALUES (0) ON DUPLICATE KEY UPDATE round_id = 0
                """
            )

        # insert initial data
        for item in config["initial_items"]:
            # insert the item
            await self.insert_item(
                item["english_name"],
                item["symbol"],
                ("", "", "", "", "", "", "", ""),
            )

            # unlock the item for all teams
            for team in config["teams"]:
                await self.unlock_item(team["team_id"], item["english_name"])

    async def unlock_item(self, team_id: int, english_name: str):
        async with DBConnection() as cnx:
            await cnx.cursor.execute(
                """
                INSERT INTO team_element_unlocked (team_id, english_name)
                SELECT %s, %s
                WHERE NOT EXISTS (
                    SELECT 1 FROM team_element_unlocked WHERE team_id = %s AND english_name = %s
                )
                """,
                (team_id, english_name, team_id, english_name),
            )

    async def insert_item(
        self,
        english_name: str,
        symbol: str,
        materials: tuple[str, str, str, str, str, str, str, str],
        team_id: int | None = None,
    ):
        materials = tuple(sorted(materials))

        async with DBConnection() as cnx:
            await cnx.cursor.execute(
                """
                INSERT INTO recipe (product_english_name, material0, material1, material2, material3, material4, material5, material6, material7)
                SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s
                WHERE NOT EXISTS (
                    SELECT 1 FROM recipe WHERE product_english_name = %s AND material0 = %s AND material1 = %s AND material2 = %s AND material3 = %s AND material4 = %s AND material5 = %s AND material6 = %s AND material7 = %s
                )
                """,
                (english_name, *materials, english_name, *materials),
            )

            await cnx.cursor.execute(
                """
                INSERT INTO element (english_name, symbol)
                SELECT %s, %s
                WHERE NOT EXISTS (
                    SELECT 1 FROM element WHERE english_name = %s
                )
                """,
                (english_name, symbol, english_name),
            )

            if team_id is not None:
                await self.unlock_item(team_id, english_name)

    async def element_exist(self, english_name: str):
        async with DBConnection() as cnx:
            await cnx.cursor.execute(
                """
                SELECT symbol FROM element WHERE english_name = %s
                """,
                (english_name,),
            )
            if len(row := await cnx.cursor.fetchall()) == 0:
                return None
            return row[0][0]

    async def craft(self, query: Query):
        team_id = await query.team_id()
        materials = query.sorted_materials

        async with DBConnection() as cnx:

            # fast check: if recipe exists and is unlocked
            await cnx.cursor.execute(
                """
                SELECT recipe.product_english_name, element.symbol
                FROM recipe
                JOIN team_element_unlocked ON recipe.product_english_name = team_element_unlocked.english_name
                JOIN element ON recipe.product_english_name = element.english_name
                WHERE
                    material0 = %s AND
                    material1 = %s AND
                    material2 = %s AND
                    material3 = %s AND
                    material4 = %s AND
                    material5 = %s AND
                    material6 = %s AND
                    material7 = %s AND
                    team_id = %s
                LIMIT 1
                """,
                (*materials, team_id),
            )

            if len(row := await cnx.cursor.fetchall()) > 0:
                return row[0]

            # check if all materials are unlocked by the team
            await cnx.cursor.execute(
                """
                SELECT COUNT(*) FROM team_element_unlocked
                WHERE team_id = %s AND (
                    english_name = %s OR
                    english_name = %s OR
                    english_name = %s OR
                    english_name = %s OR
                    english_name = %s OR
                    english_name = %s OR
                    english_name = %s OR
                    english_name = %s
                )
                LIMIT 1
                """,
                (team_id, *materials),
            )

            # check if the number of unlocked materials is equal to the number of unique materials
            if len(row := await cnx.cursor.fetchall()) == 0 or row[0][0] != len(
                set(materials)
            ):
                raise ValueError("Not all materials are unlocked")

            # query the item
            await cnx.cursor.execute(
                """
                SELECT product_english_name, element.symbol FROM recipe
                JOIN element ON recipe.product_english_name = element.english_name
                WHERE
                    material0 = %s AND
                    material1 = %s AND
                    material2 = %s AND
                    material3 = %s AND
                    material4 = %s AND
                    material5 = %s AND
                    material6 = %s AND
                    material7 = %s
                LIMIT 1
                """,
                materials,
            )

            # ignore the possibility of multiple results
            if len(row := await cnx.cursor.fetchall()) == 0:
                return None
            english_name, symbol = row[0]

        # unlock the item
        await self.unlock_item(team_id, english_name)

        return english_name, symbol

    async def get_inventory(self, team_id: int):
        async with DBConnection() as cnx:
            await cnx.cursor.execute(
                """
                SELECT element.english_name, symbol
                FROM element
                JOIN team_element_unlocked ON element.english_name = team_element_unlocked.english_name
                WHERE team_id = %s
                """,
                (team_id,),
            )

            return await cnx.cursor.fetchall()

    async def check_recipe(self, recipe: Bounty.Recipe):
        async with DBConnection() as cnx:

            await cnx.cursor.execute(
                """
                SELECT COUNT(*) FROM recipe
                WHERE
                    product_english_name = %s AND
                    material0 = %s AND
                    material1 = %s AND
                    material2 = %s AND
                    material3 = %s AND
                    material4 = %s AND
                    material5 = %s AND
                    material6 = %s AND
                    material7 = %s
                """,
                (recipe.product, *recipe.sorted_materials),
            )

            # ignore the possibility of multiple results
            if len(row := await cnx.cursor.fetchall()) > 0:
                return row[0][0] > 0

            return False

    async def get_recipe(self, team_id: int, english_name: str):
        async with DBConnection() as cnx:

            # check if all materials are unlocked by the team
            await cnx.cursor.execute(
                """
                SELECT 1 FROM team_element_unlocked
                WHERE team_id = %s AND english_name = %s
                LIMIT 1
                """,
                (team_id, english_name),
            )

            # check if the number of unlocked materials is equal to the number of unique materials
            if len(row := await cnx.cursor.fetchall()) == 0 or row[0][0] != 1:
                raise ValueError("Element not unlocked")

            await cnx.cursor.execute(
                """
                SELECT id, product_english_name, 
                material0, material1,
                material2, material3,
                material4, material5,
                material6, material7  FROM recipe
                WHERE
                    product_english_name like "%s"
                """
                % english_name
            )

            return await cnx.cursor.fetchall()

    async def get_bounty(
        self, team_id: int, round_id: int | None = None
    ) -> tuple[str, tuple[int, int], dict[int, int]] | None:
        """
        Return:
        - target_product: str
        - (length, uploaded_round_id): tuple[int, int] # the information of the bounty set by the team
        - {team_id: length}: dict[int, tuple[int, int]] # the information of the bounties submitted by other teams
        """
        async with DBConnection() as cnx:
            if round_id is None:
                round_id = await self.get_current_round()

            # get the end time of the round to filter bounties
            await cnx.cursor.execute(
                """
                SELECT end_at FROM round WHERE round_id = %s
                """,
                (round_id,),
            )
            if (
                len(row := await cnx.cursor.fetchall()) == 0
                or row[0] is None
                or row[0][0] is None
            ):
                round_end_at = datetime(2050, 1, 1)  # 50 years later
            else:
                round_end_at = row[0][0]

            # get the target product and length of the bounty
            await cnx.cursor.execute(
                """
                SELECT target_product, length, created_at
                FROM bounty
                WHERE team_id = %s AND is_submitted = FALSE AND created_at <= %s
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (team_id, round_end_at),
            )

            if len(row := await cnx.cursor.fetchall()) == 0:
                return None
            target_product, length, set_bounty_created_at = row[0]
            if target_product is None:
                return None

            # get the round_id when the bounty was set
            await cnx.cursor.execute(
                """
                SELECT round_id
                FROM round
                WHERE end_at >= %s
                ORDER BY round_id ASC
                LIMIT 1
                """,
                (set_bounty_created_at,),
            )
            if len(row := await cnx.cursor.fetchall()) == 0:
                set_bounty_round_id = round_id  # current round
            else:
                set_bounty_round_id = row[0][0]

            # get the submitted length of every other team
            await cnx.cursor.execute(
                """
                SELECT team_id, length
                FROM (
                    SELECT team_id, length,
                        ROW_NUMBER() OVER (PARTITION BY team_id ORDER BY length ASC) AS rn
                    FROM bounty
                    WHERE target_product = %s AND team_id != %s AND length < %s AND created_at <= %s
                ) AS ranked
                WHERE rn = 1
                """,
                (target_product, team_id, length, round_end_at),
            )

            result = await cnx.cursor.fetchall()
            return (
                target_product,
                (length, set_bounty_round_id),
                {team_id_: length_ for team_id_, length_ in result},
            )

    async def insert_bounty(self, bounty: Bounty, is_submitted: bool = False):
        team_id = await bounty.team_id()
        target_product = bounty.target_product
        length = bounty.length
        bounty_body = bounty.model_dump_json()

        async with DBConnection() as cnx:
            await cnx.cursor.execute(
                """
                INSERT INTO bounty (team_id, target_product, length, bounty_body, is_submitted)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (team_id, target_product, length, bounty_body, is_submitted),
            )

    async def clear_bounty(self, team_id: int):
        async with DBConnection() as cnx:
            await cnx.cursor.execute(
                """
                INSERT INTO bounty (team_id, target_product, length, bounty_body, is_submitted)
                VALUES (%s, NULL, 0, '{}', FALSE)
                """,
                (team_id,),
            )

    async def get_my_bounty_history(self, team_id: int):
        async with DBConnection() as cnx:
            await cnx.cursor.execute(
                """
                SELECT target_product, length, bounty_body, created_at, is_submitted
                FROM bounty
                WHERE team_id = %s
                ORDER BY created_at ASC
                """,
                (team_id,),
            )

            return await cnx.cursor.fetchall()

    async def get_current_round(self) -> int | None:
        async with DBConnection() as cnx:
            await cnx.cursor.execute(
                """
                SELECT MAX(round_id) FROM round
                """
            )

            if len(row := await cnx.cursor.fetchall()) > 0:
                return row[0][0]

            return None

    async def get_round_info(self, round_id: int):
        async with DBConnection() as cnx:
            await cnx.cursor.execute(
                """
                SELECT round_id, end_at, round_rank FROM round WHERE round_id = %s
                """,
                (round_id,),
            )

            if len(row := await cnx.cursor.fetchall()) == 0:
                return None

            round_id, end_at, round_rank = row[0]
            return {
                "round_id": round_id,
                "end_at": end_at,
                "round_rank": round_rank,
            }

    async def check_round_exist(self, round_id: int) -> bool:
        async with DBConnection() as cnx:
            await cnx.cursor.execute(
                """
                SELECT 1 FROM round WHERE round_id = %s
                """,
                (round_id,),
            )

            return len(await cnx.cursor.fetchall()) > 0

    async def insert_round_and_set_prev_round_end(self, round_id: int | None = None):
        async with DBConnection() as cnx:
            # make sure the operation is atomic
            await cnx.cursor.execute("START TRANSACTION")

            # if the round is the first round of the day, ignore
            # otherwise, end it
            prev_round_id = await self.get_current_round()
            if round_id is None:
                round_id = prev_round_id + 1
            if not (
                round_id in config["scoreboard"]["start_round"] or prev_round_id is None
            ):
                await cnx.cursor.execute(
                    """
                    UPDATE round SET end_at = %s WHERE round_id = %s
                    """,
                    (datetime.now(), prev_round_id),
                )

            await cnx.cursor.execute(
                """
                INSERT IGNORE INTO round (round_id) VALUES (%s)
                """,
                (round_id,),
            )

            await cnx.cursor.execute("COMMIT")

    async def set_rank(self, round_id: int, rank_str: str):
        async with DBConnection() as cnx:
            await cnx.cursor.execute(
                """
                UPDATE round SET round_rank = %s WHERE round_id = %s
                """,
                (rank_str, round_id),
            )

    async def get_rank(self, round_id: int) -> str | None:
        async with DBConnection() as cnx:
            await cnx.cursor.execute(
                """
                SELECT round_rank FROM round WHERE round_id = %s
                """,
                (round_id,),
            )

            if len(row := await cnx.cursor.fetchall()) == 0 or row[0][0] is None:
                return None

            return row[0][0]

    async def get_bounty_for_calculating_score(self, round_id: int) -> dict | None:
        """
        Return a dictionary where key is team_id and value is None or the returned value of get_bounty.
        If the round isn't finished yet, return None.
        """
        async with DBConnection() as cnx:
            # get the end time of the round
            await cnx.cursor.execute(
                """
                SELECT end_at FROM round WHERE round_id = %s
                """,
                (round_id,),
            )
            if len(row := await cnx.cursor.fetchall()) == 0 or row[0][0] is None:
                return None

            # make sure the calculating is atomic
            await cnx.cursor.execute("START TRANSACTION")

            ret = {
                team["team_id"]: await self.get_bounty(team["team_id"], round_id)
                for team in config["teams"]
            }

            await cnx.cursor.execute("COMMIT")

            return ret

    async def debug(self):
        async with DBConnection() as cnx:
            from pprint import pprint

            await cnx.cursor.execute("SELECT * FROM element")
            pprint(await cnx.cursor.fetchall())

            await cnx.cursor.execute("SELECT * FROM recipe")
            pprint(await cnx.cursor.fetchall())

            await cnx.cursor.execute("SELECT * FROM team_element_unlocked")
            pprint(await cnx.cursor.fetchall())

            await cnx.cursor.execute("SELECT * FROM bounty")
            pprint(await cnx.cursor.fetchall())

    async def debug_clear_bounty(self):
        async with DBConnection() as cnx:
            await cnx.cursor.execute("DELETE FROM bounty")
            await cnx.cursor.execute("ALTER TABLE bounty AUTO_INCREMENT = 1")

    async def debug_clear_round(self):
        # delete all rounds but keep round_id = 0
        async with DBConnection() as cnx:
            await cnx.cursor.execute("DELETE FROM round WHERE round_id > 0")
            await cnx.cursor.execute(
                "UPDATE round SET end_at = NULL, round_rank = NULL WHERE round_id = 0"
            )

    async def debug_clear_recipe(self):
        async with DBConnection() as cnx:
            await self.debug_clear_bounty()

            await cnx.cursor.execute("DELETE FROM recipe")
            await cnx.cursor.execute("ALTER TABLE recipe AUTO_INCREMENT = 1")

            await cnx.cursor.execute("DELETE FROM team_element_unlocked")
            await cnx.cursor.execute(
                "ALTER TABLE team_element_unlocked AUTO_INCREMENT = 1"
            )

            await self.create_tables()


db = DB()

