import argparse
import os
from thuonglib.recycleBin import empty_recycle_bin
from thuonglib.encrypt_decrypt_file import encrypt_file, decrypt_file
from thuonglib.c_by_hand import control_by_hand
from thuonglib.delete_folder import d_folder
from thuonglib.password_cipher import p_cipher
from thuonglib.divide_merge_file import divide_file, merge_file

def main():
    parser = argparse.ArgumentParser(
        prog="cli",
        usage="mo CMD va nhan cli --help",
        description="Chuong trinh dieu khien may tinh bang dong lenh.\n"
                    "Chuong trinh duoc viet boi Tran Dinh Thuong.\n"
                    "Email: qbquangbinh@gmail.com"
    )
    parser.add_argument("--name", "-n", help="Your name", default="Tran Dinh Thuong")
    parser.add_argument("--shutdown", "-s", action="store_true", help="Shutdown the computer")
    parser.add_argument("--restart", "-r", action="store_true", help="Restart the computer")
    parser.add_argument("--sleep", "-sl", action="store_true", help="Put the computer to sleep")
    parser.add_argument("--version", "-v", action="version", version="mycli 1.0.8", help="Show version information")
    parser.add_argument("--youtube", "-y", action="store_true", help="Open YouTube in the default web browser")
    parser.add_argument("--clean", "-c", action="store_true", help="Clean temporary files")
    parser.add_argument("--deepclean", "-dc", action="store_true", help="Xoa tat ca các tep va thu muc trong thu muc Downloads")
    parser.add_argument("--control_hand", "-ch", action="store_true", help="Dieu khien may tinh bang cu chi tay.")
    parser.add_argument("--cipher", "-ci", action="store_true", help="Ma hoa van ban")
    parser.add_argument("--encrypt_file", "-ef", action="store_true", help="Ma hoa file.")
    parser.add_argument("--decrypt_file", "-df", action="store_true", help="Giai ma file.")
    parser.add_argument("--div_mer_file", "-dmf", action="store_true", help="Chia va ghep file.")
    args = parser.parse_args()
    print(f"Hello, {args.name}!")
    if args.shutdown:
        os.system("shutdown /s /t 0")
    elif args.restart:
        os.system("shutdown /r /t 0")
    elif args.sleep:
        os.system("rundll32.exe powrprof.dll,SetSuspendState 1,1,1")
    elif args.youtube:
        os.system("start https://www.youtube.com")
    elif args.clean:
        temp_folder = os.path.join(os.getenv('SystemRoot'), 'TEMP')
        print("-" * 50)
        print(f"Xac nhan xoa cac tep va thu muc tam thoi tai thu muc: {temp_folder}")
        print("Nhan y de xoa, nhan n de bo qua.")
        user_input = input("Ban co muon xoa khong? (y/n): ").lower()
        while user_input not in ['y', 'n']:
            user_input = input("Nhap y de xoa, nhap n de bo qua: ").lower()
        if user_input == 'y':
            d_folder(temp_folder)
        else:
            print("Bo qua viec xoa tep tam thoi.")
        print("-" * 50)
        
        temp_folder = os.getenv("TEMP")
        print(f"Xac nhan xoa cac tep va thu muc tam thoi tai thu muc: {temp_folder}")
        print("Nhan y de xoa, nhan n de bo qua.")
        user_input = input("Ban co muon xoa khong? (y/n): ").lower()
        while user_input not in ['y', 'n']:
            user_input = input("Nhap y de xoa, nhap n de bo qua: ").lower()
        if user_input == 'y':
            d_folder(temp_folder)
        else:
            print("Bo qua viec xoa tep tam thoi.")
        print("-" * 50)
        
        temp_folder = os.getenv("TMP")
        print(f"Xac nhan xoa cac tep va thu muc tam thoi tai thu muc: {temp_folder}")
        print("Nhan y de xoa, nhan n de bo qua.")
        user_input = input("Ban co muon xoa khong? (y/n): ").lower()
        while user_input not in ['y', 'n']:
            user_input = input("Nhap y de xoa, nhap n de bo qua: ").lower()
        if user_input == 'y':
            d_folder(temp_folder)
        else:
            print("Bo qua viec xoa tep tam thoi.")
        print("-" * 50)

        print(f"Xac nhan xoa thung rac Recycle Bin")
        print("Nhan y de xoa, nhan n de bo qua.")
        user_input = input("Ban co muon xoa khong? (y/n): ").lower()
        while user_input not in ['y', 'n']:
            user_input = input("Nhap y de xoa, nhap n de bo qua: ").lower()
        if user_input == 'y':
            empty_recycle_bin()
        else:
            print("Bo qua viec xoa thung rac Recycle Bin.")
        print("-" * 50)
            
    elif args.deepclean:
        temp_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        print("-" * 50)
        print(f"Xac nhan xoa cac tep va thu muc tam thoi tai thu muc: {temp_folder}")
        print("Nhan y de xoa, nhan n de bo qua.")
        user_input = input("Ban co muon xoa khong? (y/n): ").lower()
        while user_input not in ['y', 'n']:
            user_input = input("Nhap y de xoa, nhap n de bo qua: ").lower()
        if user_input == 'y':
            d_folder(temp_folder)
        else:
            print("Bo qua viec xoa tep tam thoi.")
        print("-" * 50)
    elif args.control_hand:
        control_by_hand()
    elif args.cipher:
        p_cipher()
    elif args.encrypt_file:
        encrypt_file()
    elif args.decrypt_file:
        decrypt_file()
    elif args.div_mer_file:
        print("Chia va ghep file.")
        choice = input("Nhap lua chon cua ban (d/m): ").lower()
        while choice not in ['d', 'm']:
            choice = input("Nhap 'd' de chia file, 'm' de ghep file: ").lower()
        if choice == 'd':
            divide_file()
        else:
            merge_file()

if __name__ == "__main__":
    main()