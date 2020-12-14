import json, aiofiles, aiohttp, os
from discord import utils
from discord.ext import commands

# gdrive_homework is a local file in the root directory, it implements the Google Drive API
from gdrive_homework import createFolderinFolder, getFolderID, uploadFiletoFolder
# subjects.json has aliases for subjects
with open("./json_files/subjects.json", "r") as read_file:
    subject_dict = json.load(read_file)

class Drivehw(commands.Cog):
    def __init__(self, client):
        self.client = client

    # events
    @commands.Cog.listener()
    async def on_ready(self):
      print("Drivehw module has been launched")

    # commands
    @commands.command()
    async def upload(self, ctx, subject):
        print("upload initiated")
        subject_name = subject.lower()
        subject_folder_id = getFolderID(subject_dict[subject_name])
        user = ctx.author

        # date is a datetime object
        # dated_folder generates folder names like February 23, 2019 - English or November 19, 2004 - Chemistry
        date = ctx.message.created_at
        dated_folder = date.strftime(f"%B %d, %Y - {subject_name}")

        # createFolderinFolder function returns the folder ID
        if getFolderID(dated_folder) is None:
            dated_folder_id = createFolderinFolder(dated_folder, subject_folder_id)
        else:
            dated_folder_id = getFolderID(dated_folder)
        answer_filename = f"{user.name} - {dated_folder}"
        attachments_len = ctx.message.attachments.__len__()
        attachment_URLS = []

        # KEEPS TRACK OF USER UPLOAD COUNTS
        # the r before the quotes is to treat it like a raw string, the '\' before the 'u' indicates the start of
        # an eight letter unicode escape code
        with open(r"./json_files/upload_counts.json", "r+") as file:
            uploader_dict = json.load(file)
            # if the user has uploaded before, increment update count by 1
            if user.name in uploader_dict.keys():
                upload_count = uploader_dict[user.name]
                upload_count += 1
                updater = {user.name: upload_count}
            # else, if user has never uploaded before, set their update count to 1
            else:
                updater = {user.name: 1}
            uploader_dict.update(updater)
            file.seek(0)
            json.dump(uploader_dict, file)
        # END OF KEEPING TRACK OF USER UPLOAD COUNTS

        # if there are no pics/files sent, store the message itself in a .txt file in cache, upload to Google Drive
        if attachments_len == 0:
            answer_string = ctx.message.content
            answer_textfile = open(f"./cache/{answer_filename}.txt", "w+")
            answer_textfile.write(answer_string)
            answer_textfile.close()
            uploadFiletoFolder(answer_filename, f"./cache/{answer_filename}.txt", dated_folder_id)

        # to get the file name, remove 77 characters from the beginning URL
        # if there's more than one attachment, download the file, store it in cache, then upload to Google Drive
        elif attachments_len != 0:
            for i in range(attachments_len):
                attachment_URLS.append(ctx.message.attachments[i].url)
                async with aiohttp.ClientSession() as session:
                    url = attachment_URLS[i]
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            url_downloaded_filename = attachment_URLS[i]

                            # removes the first 77 characters to get the filename
                            url_downloaded_filename = url_downloaded_filename[77::]

                            open(f'.eee'
                                 f'/cache/{url_downloaded_filename}', mode='w+').close()
                            # mode='wb' is "write binary"
                            f = await aiofiles.open(f'./cache/{url_downloaded_filename}', mode='wb')
                            await f.write(await resp.read())
                            await f.close()
                        uploadFiletoFolder(answer_filename,
                                           f"./cache/{url_downloaded_filename}",
                                           dated_folder_id)

        # This gives roles to users based on upload counts
        if uploader_dict[user.name] == 5:
            server_officer_role = utils.get(ctx.guild.roles, name="Server Officer")
            await user.add_roles(server_officer_role)
            await ctx.send(f"congrats {user.name} on your first 5 uploads 🤙🤙. You've been upgraded to {str(server_officer_role)}")

        elif uploader_dict[user.name] == 15:
            server_veteran_role = utils.get(ctx.guild.roles, name="Server Veteran")
            await user.add_roles(server_veteran_role)
            await ctx.send(f"congrats {user.name} on your first 15 uploads 🤙🤙. You've been upgraded to {str(server_veteran_role)}")

        elif uploader_dict[user.name] == 25:
            server_elite_role = utils.get(ctx.guild.roles, name="Server Elite")
            await user.add_roles(server_elite_role)
            await ctx.send(f"congrats {user.name} on your first 25 uploads 🤙🤙. You've been upgraded to {str(server_elite_role)}")

        else:
            await ctx.send(f"The upload gods have graciously received your offering 🤲🤲\n Your upload count is: {uploader_dict[user.name]}")


def setup(client):
    client.add_cog(Drivehw(client))
