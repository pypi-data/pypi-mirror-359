DB_NAME = "nfs"
DATE_FORMAT = "%Y.%m.%d"

from db2_hj3415.common import connection
from db2_hj3415.common.utils import *
from db2_hj3415.common.db_ops import *

from db2_hj3415.nfs._ops import *
from db2_hj3415.nfs.models import *