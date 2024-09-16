import discord
from discord.ext import commands
from discord import app_commands
import io

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

# Variables to store channel IDs
drop_channel_id = None
order_channel_id = None
proof_channel_id = None
announce_channel_id = None  # Added for announcement channel

# Required role ID
REQUIRED_ROLE_ID = 1279750892966514772

@bot.event
async def on_ready():
    try:
        await bot.tree.sync()  # Sync commands globally
        print(f'Logged in as {bot.user.name}')
    except discord.Forbidden as e:
        print(f"Cannot sync commands: Forbidden. Check bot permissions. Error details: {e}")
    except discord.HTTPException as e:
        print(f"Cannot sync commands: {e.status} {e.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def has_required_role():
    def predicate(interaction: discord.Interaction):
        return any(role.id == REQUIRED_ROLE_ID for role in interaction.user.roles)
    return commands.check(predicate)

@bot.tree.command(name='drop', description='Drop a file into a specific channel with a message')
@app_commands.describe(
    file="Upload the file",
    message="Message to include with the drop"
)
@has_required_role()
async def drop(interaction: discord.Interaction, file: discord.Attachment, message: str):
    if drop_channel_id is None:
        await interaction.response.send_message('Drop channel is not set. Use /setchannel to set it.', ephemeral=True)
        return

    # Download the file
    file_bytes = await file.read()
    file_io = io.BytesIO(file_bytes)
    
    # Send the file and message to the drop channel
    try:
        channel = interaction.guild.get_channel(drop_channel_id)
        if channel:
            await channel.send(f"# <:stock:1283077488276275301> **__HACKERZ SHOP V2__** <:stock:1283077488276275301>\n**__DROP__**: **{message}**", file=discord.File(file_io, filename=file.filename))
            await interaction.response.send_message('File dropped successfully!', ephemeral=True)
        else:
            await interaction.response.send_message('Drop channel not found. Use /setchannel to set it.', ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f'Failed to drop the file: {e}', ephemeral=True)
        

@bot.tree.command(name='proof', description='Send proof product or event')
@app_commands.describe(
    file="Upload the screenshot",
    message="Message to include with the proof"
)
@has_required_role()
async def proof(interaction: discord.Interaction, file: discord.Attachment, message: str):
    if proof_channel_id is None:
        await interaction.response.send_message('Proof channel is not set. Use /setchannel to set it.', ephemeral=True)
        return

    # Download the file
    file_bytes = await file.read()
    file_io = io.BytesIO(file_bytes)
    
    # Send the file and message to the proof channel
    try:
        channel = interaction.guild.get_channel(proof_channel_id)
        if channel:
            embed = discord.Embed(
                title="<:stock:1283077488276275301> **__HACKERZ SHOP V2__** <:stock:1283077488276275301>",
                description=f"**__EXPLANATION__**: **{message}**",
                color=0x00ff00
            )
            embed.set_image(url="attachment://" + file.filename)
            embed.set_footer(text="Created by Hackerzzz")
            await channel.send(embed=embed, file=discord.File(file_io, filename=file.filename))
            await interaction.response.send_message('Proof sent successfully!', ephemeral=True)
        else:
            await interaction.response.send_message('Proof channel not found. Use /setchannel to set it.', ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f'Failed to send the proof: {e}', ephemeral=True)

@bot.tree.command(name='order', description='Process an order')
@app_commands.describe(
    buyer_ping="Ping the buyer",
    product="Product name",
    buy_price="Price of the product",
    payment="Payment method",
    seller_ping="Ping the seller"
)
@app_commands.choices(payment=[
    app_commands.Choice(name="Crypto", value="CRYPTO"),
    app_commands.Choice(name="Nitro", value="NITRO"),
    app_commands.Choice(name="Robux", value="ROBUX"),
    app_commands.Choice(name="Fampay", value="FAMPAY"),
    app_commands.Choice(name="Servers", value="SERVERS"),
    app_commands.Choice(name="Accounts", value="ACCOUNTS"),
    app_commands.Choice(name="Trades", value="TRADING"),
    app_commands.Choice(name="Ocash", value="OCASH"),
    app_commands.Choice(name="Other", value="OTHER")
])
@has_required_role()
async def order(interaction: discord.Interaction, buyer_ping: str, product: str, buy_price: str, payment: str, seller_ping: str):
    if order_channel_id is None:
        await interaction.response.send_message('Order channel is not set. Use /setchannel to set it.', ephemeral=True)
        return

    # Create the embed
    embed = discord.Embed(
        title="**__ORDER PROCESSED__**",
        description=(
            f"**__BUYER PING__**: {buyer_ping} <a:check_discord:1280092429013352479>\n"
            f"**__PRODUCT__**: {product} <a:check_discord:1280092429013352479>\n"
            f"**__BUY PRICE__**: {buy_price} <a:check_discord:1280092429013352479>\n"
            f"**__PAYMENT__**: {payment} <a:check_discord:1280092429013352479>\n"
            f"**__SELLER PING__**: {seller_ping} <a:check_discord:1280092429013352479>\n"
        ),
        color=0x00ff00
    )
    embed.set_footer(text="Created by Hackerzzz")
    
    # Send the embed to the order channel
    try:
        channel = interaction.guild.get_channel(order_channel_id)
        if channel:
            await channel.send(embed=embed)
            await interaction.response.send_message('Order processed successfully!', ephemeral=True)
        else:
            await interaction.response.send_message('Order channel not found. Use /setchannel to set it.', ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f'Failed to process the order: {e}', ephemeral=True)

@bot.tree.command(name='setchannel', description='Set the channels for drop, order, proof, and announcements')
@app_commands.describe(
    drop_channel="Channel for dropping files",
    order_channel="Channel for sending orders",
    proof_channel="Channel for sending proofs",
    announce_channel="Channel for sending announcements"
)
@has_required_role()
async def setchannel(interaction: discord.Interaction, drop_channel: discord.TextChannel = None, order_channel: discord.TextChannel = None, proof_channel: discord.TextChannel = None, announce_channel: discord.TextChannel = None):
    global drop_channel_id, order_channel_id, proof_channel_id, announce_channel_id
    
    response = []

    if drop_channel:
        drop_channel_id = drop_channel.id
        response.append(f'Successfully set drop channel to {drop_channel.mention}')
    
    if order_channel:
        order_channel_id = order_channel.id
        response.append(f'Successfully set order channel to {order_channel.mention}')
    
    if proof_channel:
        proof_channel_id = proof_channel.id
        response.append(f'Successfully set proof channel to {proof_channel.mention}')
    
    if announce_channel:
        announce_channel_id = announce_channel.id
        response.append(f'Successfully set announce channel to {announce_channel.mention}')

    if response:
        await interaction.response.send_message('\n'.join(response), ephemeral=True)
    else:
        await interaction.response.send_message('No channels were set. Please provide at least one channel.', ephemeral=True)

@bot.tree.command(name='announce', description='Send an announcement to the announcement channel')
@app_commands.describe(
    message="Announcement message to be sent"
)
@has_required_role()
async def announce(interaction: discord.Interaction, message: str):
    if announce_channel_id is None:
        await interaction.response.send_message('Announcement channel is not set. Use /setchannel to set it.', ephemeral=True)
        return

    try:
        channel = interaction.guild.get_channel(announce_channel_id)
        if channel:
            await channel.send(f"**{message}**")
            await interaction.response.send_message('Announcement sent successfully!', ephemeral=True)
        else:
            await interaction.response.send_message('Announcement channel not found. Use /setchannel to set it.', ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f'Failed to send the announcement: {e}', ephemeral=True)
        
@bot.tree.command(name='middleman', description='Create a private thread for exchange or trade')
@app_commands.describe(
    type="Type of service (exchange, trade)",
    provider="User providing the service",
    user="User receiving the service"
)
@has_required_role()
async def middleman(interaction: discord.Interaction, type: str, provider: discord.Member, user: discord.Member):
    # Ensure the type is valid
    if type not in ["exchange", "trade"]:
        await interaction.response.send_message('Invalid type. Choose between "exchange" and "trade".', ephemeral=True)
        return
    
    # Create a private thread
    channel = interaction.channel
    thread = await channel.create_thread(
        name=f"{type.capitalize()} - {provider.display_name} & {user.display_name}",
        type=discord.ChannelType.public_thread,
        invitable=False
    )

    # Add the users to the thread
    await thread.add_user(provider)
    await thread.add_user(user)
    await thread.add_user(interaction.user)  # Add the command executor

    # Send a message to the thread
    await thread.send(f"**__Middleman {type.capitalize()}__**\n\nProvider: {provider.mention}\nUser: {user.mention}\n\nThis thread is for the {type} transaction.")

    await interaction.response.send_message('Private thread created successfully!', ephemeral=True)
    
@bot.tree.command(name='report', description='Report a scammer')
@app_commands.describe(
    explain="Explain the scam that happened",
    user="User who scammed (optional)",
    invite="Invite link of the server (optional)",
    screenshot="Screenshot of the scam (optional)"
)
async def report(
    interaction: discord.Interaction,
    explain: str,
    user: str = "N/A",
    invite: str = "N/A",
    screenshot: discord.Attachment = None
):
    # Create the report message
    embed = discord.Embed(
        title="⚠️ **__SCAMMER__** ⚠️",
        description=(
            f"**__SCAM__**: **{explain}**\n"
            f"**__SERVER__**: {invite}\n"
            f"**__USER__**: {user}\n"
            f"**__PROOF__**: {screenshot.url if screenshot else 'N/A'}"
        ),
        color=0xff0000
    )
    
    # Set the footer with the user who reported
    embed.set_footer(text=f"Reported by {interaction.user.display_name}")

    # Send the report to a specific channel, e.g., a report channel
    report_channel = interaction.guild.get_channel(1280083799803166741)  # Set REPORT_CHANNEL_ID to your report channel's ID
    if report_channel:
        await report_channel.send(embed=embed)
        await interaction.response.send_message('Report submitted successfully!', ephemeral=True)
    else:
        await interaction.response.send_message('Report channel not found. Please contact an admin.', ephemeral=True)
        
@bot.tree.command(name='message', description='Send a message to a user')
@app_commands.describe(
    anonymous="Whether the message is anonymous (true/false)",
    user="The user to send the message to",
    message="The message to send"
)
async def message(interaction: discord.Interaction, anonymous: bool, user: discord.User, message: str):
    # Check if the user has the required role or a role above it
    role_id = 1279750644802125834
    has_permission = any(role.id >= role_id for role in interaction.user.roles)

    if not has_permission:
        await interaction.response.send_message('You do not have permission to use this command.', ephemeral=True)
        return

    # Format the message
    footer_text = "Anonymous Message" if anonymous else f"Sent by {interaction.user.name}"
    message_content = (
        f"<:stock:1283077488276275301> **__HACKERZ SHOP V2__** <:stock:1283077488276275301>\n"
        f"**__I've got a message for you__**:\n\n{message}\n"
        f"|| {footer_text} ||"
    )

    # Send the message to the user
    try:
        await user.send(message_content)
        await interaction.response.send_message('Message sent successfully!', ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f'Failed to send the message: {e}', ephemeral=True)
        
@bot.tree.command(name='add-product', description='Add a product with an optional file and subscription option')
@app_commands.describe(
    product_id="ID of the product (5 characters, numbers only)",
    title="Title of the product",
    description="Description of the product",
    channel="Channel to send the product",
    subscription="Is it a subscription-based product?",
    file="Optional file to be sent with the product (if subscription is false)"
)
@has_required_role()
async def add_product(interaction: discord.Interaction, product_id: str, title: str, description: str, channel: discord.TextChannel, subscription: bool, file: discord.Attachment = None):
    if len(product_id) != 5 or not product_id.isdigit():
        await interaction.response.send_message("Product ID must be exactly 5 digits.", ephemeral=True)
        return

    if subscription and file:
        await interaction.response.send_message("Subscription products should not include a file.", ephemeral=True)
        return

    if not subscription and file:
        file_bytes = await file.read()
        file_io = io.BytesIO(file_bytes)
        # Save file URL to be used later
        product_data[product_id] = (title, description, channel.id, file_io, subscription)
        await interaction.response.send_message(f'Product added successfully with file in {channel.mention}.', ephemeral=True)
    else:
        product_data[product_id] = (title, description, channel.id, None, subscription)
        await interaction.response.send_message(f'Product added successfully in {channel.mention}.', ephemeral=True)
        
        
@bot.tree.command(name='del-product', description='Delete a product from the store')
@app_commands.describe(
    product_id="Enter the product ID to delete"
)
@has_required_role()
async def del_product(interaction: discord.Interaction, product_id: str):
    if len(product_id) != 5 or not product_id.isdigit():
        await interaction.response.send_message('Product ID must be exactly 5 digits.', ephemeral=True)
        return

    # Iterate over all channels to find the product and delete it
    try:
        deleted = False
        for channel in interaction.guild.text_channels:
            async for message in channel.history(limit=100):  # Limit can be adjusted as needed
                if message.embeds and message.embeds[0].footer.text == f"Product ID –> {product_id}":
                    await message.delete()
                    deleted = True
                    break
            if deleted:
                break

        if deleted:
            await interaction.response.send_message(f'**__Deleted product {product_id}__**', ephemeral=True)
        else:
            await interaction.response.send_message('Product not found.', ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f'Failed to delete the product: {e}', ephemeral=True)

@bot.tree.command(name='info-product', description='Get information about a product')
@app_commands.describe(
    product_id="Enter the product ID to get details"
)
async def info_product(interaction: discord.Interaction, product_id: str):
    if len(product_id) != 5 or not product_id.isdigit():
        await interaction.response.send_message('Product ID must be exactly 5 digits.', ephemeral=True)
        return

    try:
        found = False
        for channel in interaction.guild.text_channels:
            async for message in channel.history(limit=100):  # Limit can be adjusted as needed
                if message.embeds and message.embeds[0].footer.text == f"Product ID –> {product_id}":
                    await interaction.response.send_message(embed=message.embeds[0])
                    found = True
                    break
            if found:
                break

        if not found:
            await interaction.response.send_message('Product not found.', ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f'Failed to retrieve the product info: {e}', ephemeral=True)

@bot.tree.command(name='credit', description='Provide credits to a user')
@app_commands.describe(
    user="User to provide credits",
    amount="Amount of credits to provide"
)
@has_required_role()
async def credit(interaction: discord.Interaction, user: discord.User, amount: int):
    if amount <= 0:
        await interaction.response.send_message("Amount must be greater than zero.", ephemeral=True)
        return

    if user.id in user_credits:
        user_credits[user.id] += amount
    else:
        user_credits[user.id] = amount

    await interaction.response.send_message(f'Granted {amount} credits to {user.mention}.', ephemeral=True)
    
@bot.tree.command(name='debit', description='Remove credits from a user')
@app_commands.describe(
    user="User to remove credits from",
    amount="Amount of credits to remove"
)
@has_required_role()
async def debit(interaction: discord.Interaction, user: discord.User, amount: int):
    if user.id not in user_credits or user_credits[user.id] < amount:
        await interaction.response.send_message("User does not have enough credits.", ephemeral=True)
        return

    user_credits[user.id] -= amount

    if user_credits[user.id] == 0:
        del user_credits[user.id]

    await interaction.response.send_message(f'Removed {amount} credits from {user.mention}.', ephemeral=True)
    
@bot.tree.command(name='panel', description='Send a credit panel with available products')
@app_commands.describe(
    channel="Channel to send the credit panel",
    products="Product IDs and prices (format: id:price,id:price,...)"
)
@has_required_role()
async def panel(interaction: discord.Interaction, channel: discord.TextChannel, products: str):
    product_options = []
    for item in products.split(','):
        product_id, price = item.split(':')
        if product_id in product_data:
            title, description, _, _, _ = product_data[product_id]
            product_options.append(
                discord.SelectOption(label=f"{title} - {price} credits", value=product_id)
            )

    embed = discord.Embed(
        title="HACKERZ SHOP V2",
        description="Welcome to the credit shop. Use credits to purchase available products.",
        color=0x00ff00
    )
    embed.set_footer(text="Select a product from the dropdown menu")

    # Send the panel
    try:
        select = discord.ui.Select(placeholder="Select a product", options=product_options)
        async def select_callback(interaction: discord.Interaction):
            selected_product_id = select.values[0]
            if selected_product_id in product_data:
                title, description, channel_id, file_url, _ = product_data[selected_product_id]
                if interaction.user.id in user_credits and user_credits[interaction.user.id] >= int(price):
                    user_credits[interaction.user.id] -= int(price)
                    channel = bot.get_channel(channel_id)
                    if file_url:
                        await interaction.user.send(file=discord.File(file_url, filename=f"{title}.file"))
                    await interaction.user.send(embed=discord.Embed(
                        title=title,
                        description=description,
                        color=0x00ff00
                    ))
                    await interaction.response.send_message("Product sent to your DMs!", ephemeral=True)
                else:
                    await interaction.response.send_message("Insufficient credits.", ephemeral=True)

        view = discord.ui.View()
        view.add_item(select)
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message(f'Credit panel sent to {channel.mention}.', ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f'Failed to send credit panel: {e}', ephemeral=True)
        
bot.run('')