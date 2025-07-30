# Copyright (C) 2025 Neongecko.com Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from os import environ
from neon_users_service.mq_connector import NeonUsersConnector
from ovos_utils import wait_for_exit_signal
from ovos_utils.log import LOG, init_service_logger
from neon_utils.process_utils import start_health_check_server

init_service_logger("neon-users-service")


def main():
    connector = NeonUsersConnector(None)
    LOG.info("Starting Neon Users Service")
    if status_port := environ.get("HEALTHCHECK_PORT"):
        start_health_check_server(
            connector.status, int(status_port), connector.check_health
        )
    connector.run()
    LOG.info("Started Neon Users Service")
    wait_for_exit_signal()
    LOG.info("Shut down")


if __name__ == "__main__":
    main()
