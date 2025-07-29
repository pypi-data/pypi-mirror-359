import os
from typing import Union

class IrapSeq:
	def __init__(self) -> None:
		self.module_dir: str = os.path.dirname(os.path.abspath(__file__))
		self.irap_path: str = os.path.join(self.module_dir, 'irap.txt')
		self.irap_dict: dict = self.__readirap__()
	
	def __readirap__(self) -> dict[str, str]:
		irap: dict[str, str] = dict()
		with open(self.irap_path, 'r') as file:
			for line in file:
				line = line.strip().split(' ')
				the_type: str = line[1]
				the_size: str = line[3]
				context: str = line[-1]
				name = f'type:{the_type}+size:{the_size}'
				irap[name] = context
		return irap
		
	def irap_dict(self, type:str, size: str) -> str:
		name: str = f'type:{type}+size:{size}'
		return self.irap_dict[name]
	
	def irap_dicts(self) -> dict[str, str]:
		return self.irap_dict
		
	def irap(self, seq:str, type_and_size: Union[bool, str] = None) -> str:
		if type_and_size:
			name: str = type_and_size
		else:
			name: str = f'type:0+size:1'
		irap_context: list = self.irap_dict[name].split("-")
		return self.__seqtoirap__(seq.upper(), irap_context)
		
	@staticmethod
	def __seqtoirap__(seq: str, irap_list: list) -> str:
		irap_seq: str = ''
		for res in seq:
			for irap_type in irap_list:
				if res in irap_type:
					irap_seq += irap_type[0]
		return irap_seq


if __name__ == '__main__':
    irap_str = "LVIMCAGSTPFYW-EDNQKRH"
    fasta_file: str = './cd_hit_ready.fasta'
    # main(fasta_file, irap_str)
    a = IrapSeq()
    types = a.irap_dicts()
    for k, v in types.items():
	    
        print(a.irap(seq='eeewe', type_and_size=k))