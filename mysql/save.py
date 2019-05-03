from jiaotyubao.mysql.save_course import save_course
from jiaoyubao.mysql.save_school import save_school


#sid和cid为数据库school表和course表对应起始id
save_school('jiaoyubao_school:items', sid, 0, -1)
save_course('jiaoyubao_course:items', cid, 0, -1)
