import re


class NumberUtil:
    @staticmethod
    def to_int(src: str | None, fallback: int | None = 0) -> int | None:
        '''문자열을 정수로 변경'''
        if not src:
            return fallback
        unit = 10000 if src.endswith('만원') else 1
        find = re.findall(pattern=r'\d+', string=src)
        return int(''.join(find)) * unit if find is not None and len(find) > 0 else fallback

    @staticmethod
    def find_percent(src: str, fallback: int | None = 0) -> int | None:
        '''문자열에 퍼센트 찾기'''
        find = re.search(r'\d+%', src)
        return int(find.group().replace('%', '')) if find is not None else fallback

    @staticmethod
    def find_area(src: str | None, fallback: int | None = None) -> float | None:
        '''문자열에서 면적 찾기'''
        if not src:
            return fallback
        find = re.findall(r'\d+\.?\d*(?=㎡)', src)
        return sum(map(lambda x: float(re.sub(r'[^0-9.]', '', x).strip().replace(')', '')), find)) if find else fallback
