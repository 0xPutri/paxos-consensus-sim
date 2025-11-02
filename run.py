from typing import Any, Optional, List


class Acceptor:

    def __init__(self, name: str) -> None:
        """Inisialisasi acceptor Paxos.

        Args:
            name (str): Nama unik acceptor untuk identifikasi log.
        """
        self.name: str = name
        self.promised_number: Optional[int] = None
        self.accepted_value: Optional[Any] = None

    def prepare(self, proposal_number: int) -> tuple[bool, Optional[Any]]:
        """Menangani fase PREPARE Paxos.

        Menerima promise jika `proposal_number` ≥ janji sebelumnya.
        
        Args:
            proposal_number (int): Nomor proposal dari proposer.

        Returns:
            tuple[bool, Optional[Any]]: (Berhasil memberi promise?, nilai diterima sebelumnya).
        """
        if self.promised_number is None or proposal_number > self.promised_number:
            self.promised_number = proposal_number
            print(f"[PREPARE] {self.name} menerima promise untuk proposal #{proposal_number}")
            return True, self.accepted_value
        
        print(
            f"[PREPARE] {self.name} menolak proposal #{proposal_number} "
            f"(sudah janji pada proposal #{self.promised_number})"
        )
        return False, self.accepted_value
    
    def accept(self, proposal_number: int, value: Any) -> bool:
        """Menangani fase ACCEPT Paxos.

        Menerima nilai hanya jika `proposal_number` ≥ janji terakhir.
        
        Args:
            proposal_number (int): Nomor proposal.
            value (Any): Nilai yang diusulkan.

        Returns:
            bool: True jika nilai diterima, False jika ditolak.
        """
        if self.promised_number is None or proposal_number >= self.promised_number:
            self.promised_number = proposal_number
            self.accepted_value = value

            print(f"[ACCEPT] {self.name} menerima nilai '{value}' pada proposal #{proposal_number}")
            return True
        
        print(
            f"[ACCEPT] {self.name} menolak nilai '{value}' "
            f"(proposal #{proposal_number} < promise #{self.promised_number})"
        )
        return False


class Proposer:

    def __init__(self, proposal_number: int, value: Any) -> None:
        """Inisialisasi proposer Paxos.

        Args:
            proposal_number (int): Nomor unik proposal (harus monoton meningkat).
            value (Any): Nilai yang akan diusulkan jika tidak ada nilai sebelumnya.
        """
        self.proposal_number: int = proposal_number
        self.value: Any = value

    def propose(self, acceptors: List[Acceptor]) -> Optional[Any]:
        """Jalankan dua fase Paxos untuk capai konsensus.

        Fase 1: Kirim PREPARE ke semua acceptor, kumpulkan promise.
        Fase 2: Jika mayoritas merespons, kirim ACCEPT dengan nilai
        terakhir yang diterima (atau nilai awal jika belum ada).
        
        Args:
            acceptors (List[Acceptor]): Daftar acceptor peserta.

        Returns:
            Optional[Any]: Nilai konsensus jika mayoritas menerima, None jika gagal.
        """
        print(f"Proposer mengajukan proposal #{self.proposal_number} dengan nilai '{self.value}'")

        print("Phase 1: PREPARE")
        promise_count = 0
        previous_values: list[Any] = []

        for acc in acceptors:
            ok, prev = acc.prepare(self.proposal_number)
            if ok:
                promise_count += 1
            if prev is not None:
                previous_values.append(prev)

        print(f"Total promise: {promise_count} dari {len(acceptors)}")

        if promise_count < (len(acceptors) // 2 + 1):
            print("Konsensus gagal pada fase PREPARE (tidak ada mayoritas)")
            return None
        
        if previous_values:
            final_value = previous_values[-1]
        else:
            final_value = self.value

        print("Phase 2: ACCEPT")
        accept_count = 0
        for acc in acceptors:
            if acc.accept(self.proposal_number, final_value):
                accept_count += 1

        print(f"Total accept: {accept_count} dari {len(acceptors)}")

        if accept_count >= (len(acceptors) // 2 + 1):
            print(f"Konsensus berhasil. Nilai: '{final_value}'")
            return final_value
        
        print("Konsensus gagal pada fase ACCEPT (tidak ada mayoritas)")
        return None


def main() -> None:
    """Jalankan simulasi Paxos dengan 5 acceptor dan 1 proposer."""
    acceptors = [Acceptor("A"), Acceptor("B"), Acceptor("C"), Acceptor("D"), Acceptor("E")]

    """acceptors[0].promised_number = 5
    acceptors[1].promised_number = 5
    acceptors[2].promised_number = 5"""

    proposer = Proposer(proposal_number=1, value="BLOCK-001")
    proposer.propose(acceptors)


if __name__ == '__main__':
    main()