from mcp.server.fastmcp import FastMCP

mcp = FastMCP("My awsome server")


@mcp.tool()
def return_fahad():
    """A tool to return about who Fahad Khan is."""
    return "Fahad is one the best gen ai developers. Booo Yaaa ! Sucess !!"

def main ():
    mcp.run()
if __name__ == "__main__":
    main()

