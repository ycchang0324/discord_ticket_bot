import discord
import asyncio
from src.utility import login, logout, getImage, get_ticket_num, check_ticket_num, BrowserCriticalError
import os

async def get_ticket(bot, interaction: discord.Interaction, category, driver, your_web_url, your_account, your_password, target_channel_ids, target_channel_name, maintainer_id_env):
    
    # 1. 初始定義變數，防止 finally 找不到
    finish_messages_dict = {} 
    welcome_messages_dict = {}
    
    # 1. 全域狀態檢查
    if bot.is_ticket_generating:
        # 如果已經 defer 過，要用 followup
        await interaction.followup.send("⚠️ 目前已有票卷正在生成中，請稍候約 5 分鐘再試。", ephemeral=True)
        return

    # interaction.user 取代 ctx.author
    sender_name = interaction.user.display_name

    # interaction.channel_id 取代 ctx.channel.id
    if str(interaction.channel_id) in target_channel_ids:
        
        try:
            # 2. 鎖定狀態
            bot.is_ticket_generating = True
            
            # 使用 interaction.response.send_message
            await interaction.followup.send(f"{sender_name} 您好，請稍等 30 秒~", ephemeral=True)
            
            welcome_messages_dict = {}
            for channel_id in target_channel_ids:
                channel = bot.get_channel(int(channel_id))
                if channel:
                    sent_message = await channel.send("努力生成票卷 QR Code 中~~請先不要傳訊息給我，不然我會不理你，稍等大概五分鐘喔！")
                    welcome_messages_dict[int(channel_id)] = sent_message
                else:
                    print(f'無法找到頻道 {channel_id}')    
            
            if not await login(driver, your_web_url, your_account, your_password):
                # 這裡改用 followup 因為 response 已經用過了
                channel = bot.get_channel(int(interaction.channel_id))
                if channel:
                    await channel.send("登入系統時出現問題")
                return
            
            await getImage(driver, category)

            res_num = get_ticket_num(driver, category)
            if res_num is None:
                channel = bot.get_channel(int(interaction.channel_id))
                if channel:
                    await channel.send("獲取票卷張數時出現問題")
                return
            else:        
                ticket_num = int(res_num)

            # 確認票卷數量
            if ticket_num < 2:
                channel = bot.get_channel(int(interaction.channel_id))
                if channel: await channel.send(f"{category} 票卷不足，請加值><")
            else:
                if ticket_num < 6:
                    # 頻道廣播訊息依然用 channel.send
                    channel = bot.get_channel(int(interaction.channel_id))
                    if channel: await channel.send(f"{category} 票卷即將不足，請加值><")
                
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                image_path = os.path.join(base_dir, 'img', 'screenshot_crop.png')
                empty_path = os.path.join(base_dir, 'img', 'empty.png')
                
                picture = discord.File(image_path, filename="screenshot_crop.png")
                empty_pic = discord.File(empty_path, filename="empty.png")
                
                # 更新原本的延遲訊息 (edit_original_response)
                await interaction.edit_original_response(content=f"已傳送 {category} QR Code，請在三分鐘之內使用喔", attachments=[picture])

                success = await check_ticket_num(driver, ticket_num, category)
                if success is None:
                    channel = bot.get_channel(int(interaction.channel_id))
                    if channel:
                        await channel.send("獲取票卷張數時出現問題")
                    return
                
            
                user = await bot.fetch_user(int(maintainer_id_env))

                if success:
                    # 更新訊息為成功 (注意 attachments 傳入空列表或新圖片)
                    await interaction.edit_original_response(content=f"{sender_name} 已成功使用 {category} 票卷！ \n\n 再請你匯款、Line Pay 或是街口支付了，詳細資訊可以發送 /help 來獲取喔", attachments=[empty_pic])
                    ticket_num = ticket_num - 1
                    
                    
                    if user:
                        try:
                            await user.send(f"{sender_name} 成功使用 {category} QR Code，剩餘 {ticket_num} 張")
                        except Exception as e:
                            print(f"私訊失敗: {e}")

                else:
                    await interaction.edit_original_response(content=f"{sender_name} 未使用 {category} QR Code，請重新生成><", attachments=[empty_pic])
                    
                    if user:
                        try:
                            await user.send(f"{sender_name} 未使用 {category} QR Code，剩餘 {ticket_num} 張")
                        except Exception as e:
                            print(f"私訊失敗: {e}")

            # 清理 welcome 訊息
            for sent_message in welcome_messages_dict.values():
                await sent_message.delete()
            
            if not await logout(driver):
                print("登出系統時出現問題")

            finish_messages_dict = {}
            for channel_id in target_channel_ids:
                channel = bot.get_channel(int(channel_id))
                if channel:
                    sent_message = await channel.send("結束生成。可以再次呼喚我了喔")
                    finish_messages_dict[int(channel_id)] = sent_message
            
            
            

        except BrowserCriticalError as e:
            print(f"發生錯誤: {e}")
            # 如果發生錯誤，確保能透過 followup 告知使用者
            try:
                channel = bot.get_channel(int(interaction.channel_id))
                if channel:
                    await channel.send("程式執行中發生錯誤，請聯絡管理員。")
            except:
                pass
        finally:
            # 5. 無論如何都解鎖
            bot.is_ticket_generating = False
            
            # 使用背景任務處理 60 秒後的刪除，不影響主邏輯
            async def delayed_delete(msgs):
                await asyncio.sleep(60)
                for m in msgs:
                    try: await m.delete()
                    except: pass
            
            if finish_messages_dict:
                asyncio.create_task(delayed_delete(finish_messages_dict.values()))
        
    else:
        # 頻道不對的回應
        await interaction.response.send_message(f"請在 **{target_channel_name}** 頻道中發送 **/給我{category}票** 以索取 {category} QR Code 喔", ephemeral=True)