import discord
import asyncio
from src.utility import log_to_file, login, logout, getImage, get_ticket_num, check_ticket_num
import os

async def get_ticket(bot, ctx, category, driver, your_web_url, your_account, your_password, target_channel_ids, target_channel_name, maintainer_id_env):
    

    sender_name = ctx.author.display_name

    if str(ctx.channel.id) in target_channel_ids:
        

        await ctx.respond(f"{sender_name} 您好，請稍等 15 秒~", ephemeral=True)
        welcome_messages_dict = {}
        for channel_id in target_channel_ids:
        # 獲取頻道對象並存入字典中
            channel = bot.get_channel(int(channel_id))
            if channel :
                # 發送訊息並儲存訊息對象
                sent_message = await channel.send("努力生成票卷 QR Code 中~~請先不要傳訊息給我，不然我會不理你，稍等大概五分鐘喔！")
                welcome_messages_dict[int(channel_id)] = sent_message
            else:
                print(f'無法找到頻道 {channel_id}')    
        
        if not login(driver, your_web_url, your_account, your_password):
            await ctx.channel.send("登入系統時出現問題")
            return
        
        getImage(driver, category)

        if get_ticket_num(driver,category) == None:
            await ctx.channel.send("獲取票卷張數時出現問題")
            return
        else:        
            ticket_num = int(get_ticket_num(driver, category))

        #確認票卷數量
        if ticket_num < 2:
            await ctx.channel.send(f"{category} 票卷不足，請加值><")
        else:
            if ticket_num < 6:
                await ctx.channel.send(f"{category} 票卷即將不足，請加值><")
            
            
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            image_path = os.path.join(base_dir, 'img', 'screenshot_crop.png')
            empty_path = os.path.join(base_dir, 'img', 'empty.png')
            picture = discord.File(image_path, filename="screenshot_crop.png")
            empty_pic = discord.File(empty_path, filename="empty.png")
            
            await ctx.interaction.edit_original_response(content=f"已傳送 {category} QR Code，請在三分鐘之內使用喔", file=picture)

            success = check_ticket_num(driver, ticket_num, category)
            if success == None:
                await ctx.channel.send("獲取票卷張數時出現問題")
                return
            
            usage_path = os.path.join(base_dir, 'log', 'usage.txt')
            user = await bot.fetch_user(int(maintainer_id_env))

            if success:
                await ctx.interaction.edit_original_response(content=f"{sender_name} 已成功使用 {category} 票卷！ \n\n 再請你匯款或是街口支付了，詳細資訊可以發送 /help 來獲取喔", file=empty_pic)
                ticket_num = ticket_num - 1
                log_to_file(f"{sender_name} 成功使用 {category} QR Code，剩餘 {ticket_num} 張", usage_path)
                
                # 傳送使用資訊給維護者
                try:
                    if user:
                        # 2. 對 User 物件使用 send 方法發送私訊
                        await user.send(f"{sender_name} 成功使用 {category} QR Code，剩餘 {ticket_num} 張")
                        print(f"成功發送私訊給 {user.name} ({user})")
                    else:
                        print(f"找不到 ID 為 {user} 的使用者。")

                except discord.Forbidden:
                    # 如果使用者設定了隱私不接收來自非朋友的私訊，會拋出 Forbidden 錯誤
                    print(f"無法發送私訊給 ID 為 {user} 的使用者，可能因為隱私設定阻擋。")
                except Exception as e:
                    print(f"發送私訊時發生錯誤: {e}")
                # --- 私訊發送邏輯結束 ---

            else:
                await ctx.interaction.edit_original_response(content=f"{sender_name} 未使用 {category} QR Code，請重新生成><", file=empty_pic)
                log_to_file(f"{sender_name} 未使用 {category} QR Code，剩餘 {ticket_num} 張", usage_path)

                # 傳送使用資訊給維護者
                try:
                    if user:
                        # 2. 對 User 物件使用 send 方法發送私訊
                        await user.send(f"{sender_name} 未使用 {category} QR Code，剩餘 {ticket_num} 張")
                        print(f"成功發送私訊給 {user.name} ({user})")
                    else:
                        print(f"找不到 ID 為 {user} 的使用者。")

                except discord.Forbidden:
                    # 如果使用者設定了隱私不接收來自非朋友的私訊，會拋出 Forbidden 錯誤
                    print(f"無法發送私訊給 ID 為 {user} 的使用者，可能因為隱私設定阻擋。")
                except Exception as e:
                    print(f"發送私訊時發生錯誤: {e}")
                # --- 私訊發送邏輯結束 ---



        for channel_id, sent_message in  welcome_messages_dict.items():
            await sent_message.delete()
        
        if not logout(driver):
            await ctx.channel.send("登出系統時出現問題")

        finish_messages_dict = {}
        for channel_id in target_channel_ids:
        # 獲取頻道對象並存入字典中
            channel = bot.get_channel(int(channel_id))
            if channel :
                # 發送訊息並儲存訊息對象
                sent_message = await channel.send("結束生成。可以再次呼喚我了喔")
                finish_messages_dict[int(channel_id)] = sent_message
            else:
                print(f'無法找到頻道 {channel_id}')  

        await asyncio.sleep(60)
        for channel_id, sent_message in  finish_messages_dict.items():
            await sent_message.delete()
        
        
    else:
        await ctx.respond(f"請在 **{target_channel_name}** 頻道中發送 **/給我{category}票** 以索取 {category} QR Code 喔", ephemeral=True)
